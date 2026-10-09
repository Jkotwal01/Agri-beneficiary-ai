"""
ResolutionService — orchestrates the full entity resolution pipeline.

Flow:
  1. Load all clean_records from DB → Record objects
  2. Run PhoneticVillageBlocker → candidate pairs
  3. For each pair: score with XGBoostPairMatcher → save MatchCandidate
  4. Collect auto_link pairs → build_clusters
  5. For each cluster: chain guard → create Farmer golden record + FarmerLink rows
  6. Return ResolutionSummary
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.clean_record import CleanRecord
from app.models.farmer import Farmer
from app.models.farmer_link import FarmerLink
from app.models.match_candidate import MatchCandidate
from app.models.source_record import SourceRecord
from app.resolution.blocking import PhoneticVillageBlocker, Record
from app.resolution.clustering import build_clusters, passes_chain_guard
from app.resolution.golden_record import TrustOrderGoldenRecordBuilder
from app.resolution.matcher import XGBoostPairMatcher
from app.schemas.resolution import ResolutionSummary


class ResolutionService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._blocker = PhoneticVillageBlocker()
        self._matcher = XGBoostPairMatcher()
        self._golden_builder = TrustOrderGoldenRecordBuilder()

    def run(self) -> ResolutionSummary:
        db = self._db

        # ------------------------------------------------------------------ #
        # Step 1: Load clean_records and source mapping
        # ------------------------------------------------------------------ #
        clean_rows = db.query(CleanRecord).all()
        records: list[Record] = []
        source_map: dict[int, str] = {}  # clean_record.id → data_source

        # Build a source_record id → data_source lookup
        src_lookup: dict[int, str] = {
            sr.id: (sr.source_name or "") for sr in db.query(SourceRecord).all()
        }

        for row in clean_rows:
            rec = Record(
                id=row.id,
                name_norm=row.name_norm,
                father_norm=row.father_norm,
                name_phonetic=row.name_phonetic,
                mobile10=row.mobile10,
                village_code=row.village_code,
                district_code=row.district_code,
                survey_no=row.survey_no,
                dob=row.dob,
                bank_last4=row.bank_last4,
                crop=row.crop,
                season=row.season,
            )
            records.append(rec)
            source_map[row.id] = src_lookup.get(row.source_record_id, "")

        record_map: dict[int, Record] = {r.id: r for r in records}

        # ------------------------------------------------------------------ #
        # Step 2: Blocking
        # ------------------------------------------------------------------ #
        candidate_pairs = self._blocker.candidate_pairs(records)

        # ------------------------------------------------------------------ #
        # Step 3: Score each pair and persist MatchCandidate
        # ------------------------------------------------------------------ #
        # Clear existing match_candidates for a clean run
        db.query(MatchCandidate).delete()
        db.flush()

        auto_links: list[tuple[int, int, float]] = []
        stats = {"auto_link": 0, "review": 0, "no_match": 0}

        for id_a, id_b in candidate_pairs:
            rec_a = record_map.get(id_a)
            rec_b = record_map.get(id_b)
            if not rec_a or not rec_b:
                continue

            sc, fv, decision = self._matcher.score_with_decision(rec_a, rec_b)

            mc = MatchCandidate(
                record_a=id_a,
                record_b=id_b,
                score=sc,
                decision=decision,
                features_json=fv,
            )
            db.add(mc)
            stats[decision] = stats.get(decision, 0) + 1

            if decision == "auto_link":
                auto_links.append((id_a, id_b, sc))

        db.flush()

        # ------------------------------------------------------------------ #
        # Step 4: Clustering
        # ------------------------------------------------------------------ #
        link_pairs = [(a, b) for a, b, _ in auto_links]
        # Average score per cluster for confidence
        score_by_pair: dict[tuple[int, int], float] = {
            (a, b): sc for a, b, sc in auto_links
        }

        clusters = build_clusters(link_pairs, source_map)

        # Also include singletons (records not in any auto_link)
        all_linked_ids: set[int] = {rid for cluster in clusters for rid in cluster}
        singletons = [[rid] for rid in record_map if rid not in all_linked_ids]

        # ------------------------------------------------------------------ #
        # Step 5: Build Farmer golden records
        # ------------------------------------------------------------------ #
        # Wipe existing farmers + links for clean run
        db.query(FarmerLink).delete()
        db.query(Farmer).delete()
        db.flush()

        farmers_created = 0
        chain_guard_blocked = 0

        all_clusters = clusters + singletons

        for cluster in all_clusters:
            ok, _ = passes_chain_guard(cluster, source_map)
            if not ok and len(cluster) > 1:
                chain_guard_blocked += 1
                # Treat each record as its own singleton
                for rid in cluster:
                    all_clusters.append([rid])
                continue

            # Average score across pairs in this cluster
            pair_scores = [
                score_by_pair.get((min(a, b), max(a, b)), 0.0)
                for i, a in enumerate(cluster)
                for b in cluster[i + 1 :]
            ]
            confidence = sum(pair_scores) / len(pair_scores) if pair_scores else 1.0

            record_source_pairs = [
                (record_map[rid], source_map.get(rid, ""))
                for rid in cluster
                if rid in record_map
            ]
            if not record_source_pairs:
                continue

            golden = self._golden_builder.build(record_source_pairs, confidence)

            farmer = Farmer(
                name=golden.get("name_norm") or "Unknown",
                father_name=golden.get("father_norm"),
                dob=golden.get("dob"),
                mobile=golden.get("mobile10"),
                village_code=golden.get("village_code"),
                district_code=golden.get("district_code"),
                total_land_ha=None,
                category=None,
                confidence=golden.get("confidence", 1.0),
            )
            db.add(farmer)
            db.flush()

            for rid in cluster:
                if rid not in record_map:
                    continue
                link = FarmerLink(
                    farmer_id=farmer.id,
                    clean_record_id=rid,
                    method="auto_link" if len(cluster) > 1 else "singleton",
                    score=confidence if len(cluster) > 1 else None,
                )
                db.add(link)

            farmers_created += 1

        db.commit()

        return ResolutionSummary(
            clean_records_processed=len(records),
            candidate_pairs_evaluated=len(candidate_pairs),
            auto_linked=stats.get("auto_link", 0),
            flagged_for_review=stats.get("review", 0),
            no_match=stats.get("no_match", 0),
            farmers_created=farmers_created,
            chain_guard_blocked=chain_guard_blocked,
        )
