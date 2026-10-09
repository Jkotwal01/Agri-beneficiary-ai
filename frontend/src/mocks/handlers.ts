import { http, HttpResponse } from 'msw';

// Mock Farmers Data
const mockFarmers = Array.from({ length: 50 }).map((_, i) => ({
  id: 1000 + i,
  name: i % 3 === 0 ? `Ramesh Kumar ${i}` : `Suresh Singh ${i}`,
  district_code: ['PUNE', 'NASHIK', 'NAGPUR'][i % 3],
  village_code: `VIL-${i % 5}`,
  confidence: i % 4 === 0 ? 0.85 : 0.99,
  mobile: `9876543${i.toString().padStart(3, '0')}`,
  total_land_ha: (Math.random() * 5).toFixed(2),
  agristack_id: `AS-${i}XYZ`,
  pmkisan_id: i % 2 === 0 ? `PK-${i}ABC` : null,
  pmfby_id: i % 3 === 0 ? `PF-${i}DEF` : null,
  kcc_id: i % 4 === 0 ? `KC-${i}GHI` : null,
  status: i % 5 === 0 ? 'Review' : 'Golden',
}));

export const handlers = [
  // 1. Dashboard Summary
  http.get('*/api/reports/summary', () => {
    return HttpResponse.json({
      total_ingested: 12470,
      golden_records: 4892,
      active_flags: 134,
      pending_reviews: 45,
    });
  }),

  // 2. Farmers List
  http.get('*/api/farmers', ({ request }) => {
    const url = new URL(request.url);
    const q = url.searchParams.get('q') || '';
    
    let results = mockFarmers;
    if (q) {
      results = results.filter(f => f.name.toLowerCase().includes(q.toLowerCase()));
    }
    
    return HttpResponse.json({
      items: results.slice(0, 50),
      total: results.length,
    });
  }),

  // 3. Review Queue
  http.get('*/api/matches', ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get('decision') === 'review') {
      return HttpResponse.json({
        items: [
          {
            id: 101,
            score: 0.72,
            record_a: { source: 'AGRISTACK', name_norm: 'ramesh kumar', mobile10: '9876543210', district_code: 'PUNE', survey_no: '45/A', dob: '1985-05-12' },
            record_b: { source: 'PM_KISAN', name_norm: 'ramesh k', mobile10: '9876543210', district_code: 'PUNE', survey_no: '45/B', dob: '1985-05-12' },
            features: {
              name_jw: 0.88,
              same_mobile: 1,
              survey_match: 0,
              district_match: 1,
              dob_match: 1,
            },
            shap: [
              { feature: 'same_mobile', value: '1', shap_value: 1.2 },
              { feature: 'name_jw', value: '0.88', shap_value: 0.8 },
              { feature: 'survey_match', value: '0', shap_value: -0.5 },
            ]
          },
          {
            id: 102,
            score: 0.65,
            record_a: { source: 'PMFBY', name_norm: 'suresh patil', mobile10: '9111111111', district_code: 'NASHIK', survey_no: '12', dob: null },
            record_b: { source: 'NFSM', name_norm: 'suresh patil', mobile10: '9000000000', district_code: 'NASHIK', survey_no: '12', dob: '1990-01-01' },
            features: {
              name_jw: 1.0,
              same_mobile: 0,
              survey_match: 1,
              district_match: 1,
              dob_match: -1,
            },
            shap: [
              { feature: 'name_jw', value: '1.0', shap_value: 1.0 },
              { feature: 'survey_match', value: '1', shap_value: 0.6 },
              { feature: 'same_mobile', value: '0', shap_value: -0.9 },
            ]
          }
        ],
        total: 2,
      });
    }
    return HttpResponse.json({ items: [], total: 0 });
  }),

  // 4. Flags/Rules Engine
  http.get('*/api/flags', () => {
    return HttpResponse.json({
      items: [
        { id: 1, farmer_id: 1005, farmer_name: 'Anil Desai', type: 'SameSchemeTwice', severity: 'HIGH', status: 'open', details: 'Found 2 active PM-KISAN enrollments in Rabi 2025.' },
        { id: 2, farmer_id: 1012, farmer_name: 'Priya Sharma', type: 'ParcelOverclaim', severity: 'MEDIUM', status: 'open', details: 'Total claimed land (3.5 Ha) exceeds survey parcel size (2.0 Ha).' },
      ],
      total: 2,
    });
  }),
];
