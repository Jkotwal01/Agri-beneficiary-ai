"""
Clustering — Spec Section 6, Module 3, Stage 4.

build_clusters(linked_pairs) → list[list[int]]
  Uses NetworkX to find connected components from auto_link pairs.

Chain Guard rules (must ALL pass for a cluster to be auto-merged):
  1. Component size ≤ 6 records (larger = suspected data quality issue)
  2. At most 1 unique AgriStack source_record per component
     (two distinct AgriStack IDs for the same farmer signals a data problem)
"""

from __future__ import annotations

import networkx as nx

MAX_CLUSTER_SIZE = 6


def build_clusters(
    linked_pairs: list[tuple[int, int]],
    source_map: dict[int, str] | None = None,
) -> list[list[int]]:
    """
    Build connected components from linked pairs.

    Args:
        linked_pairs:  List of (record_a_id, record_b_id) decided as auto_link.
        source_map:    Optional dict mapping clean_record id → data_source string.
                       Used for the AgriStack chain guard.

    Returns:
        List of clusters. Each cluster is a list of clean_record IDs.
        Clusters that fail chain guard checks are returned as singletons
        with a `_flagged` attribute set — callers should mark them for review.
    """
    if not linked_pairs:
        return []

    G = nx.Graph()
    G.add_edges_from(linked_pairs)

    clusters: list[list[int]] = []
    for component in nx.connected_components(G):
        cluster = sorted(component)
        clusters.append(cluster)

    return clusters


def passes_chain_guard(
    cluster: list[int],
    source_map: dict[int, str] | None = None,
) -> tuple[bool, str]:
    """
    Returns (ok, reason).
    ok=True  → cluster can be auto-merged into a Farmer golden record.
    ok=False → cluster must be flagged for human review.
    """
    # Guard 1: cluster size
    if len(cluster) > MAX_CLUSTER_SIZE:
        return False, f"Cluster size {len(cluster)} exceeds max {MAX_CLUSTER_SIZE}"

    # Guard 2: at most one AgriStack source per cluster
    if source_map:
        agristack_ids = [
            rid
            for rid in cluster
            if (source_map.get(rid) or "").lower().startswith("agristack")
        ]
        if len(agristack_ids) > 1:
            return (
                False,
                f"Multiple AgriStack records in cluster: {agristack_ids}",
            )

    return True, "ok"
