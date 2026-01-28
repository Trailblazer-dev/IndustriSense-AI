# FEASIBILITY SUMMARY TABLE - IndustriSense-AI

## Quick Reference: Requirements Feasibility Status

| Requirement | Status | Evidence Source | Recommended Action |
| --- | --- | --- | --- |
| FR-1: Feature Mapping | ✓ FEASIBLE | All required sensor features present in dataset | Proceed with implementation |
| FR-2: Isolation Forest Anomaly Detection | ◐ PARTIALLY FEASIBLE | Can detect cross-sectional outliers; temporal drift detection requires sequences | Reframe as cross-sectional outlier detection; defer temporal drift to Phase 2 |
| FR-3: Stress Index Feature | ✓ FEASIBLE | EDA validates strong discriminative power (2.85x mean difference between OSF/no-OSF cases) | Proceed; add statistical significance tests (ANOVA, effect size) |
| FR-4: Thermal Trend (slope over time) | ✗ NOT FEASIBLE | Dataset is static snapshot with no timestamps or machine sequence IDs; EDA explicitly notes impossibility | Replace with Temperature Differential feature (calculable from current data); document thermal trend as Phase 2 enhancement requiring real-time data |
| FR-5: XGBoost Failure Classification | ✓ FEASIBLE | 10,000 labeled examples with 339 failures; failure modes show distinct sensor signatures in EDA | Proceed; implement class weighting (0.97:0.03 ratio) and validate Recall ≥ 0.95 |
| FR-6: CLSTM RUL Prognosis | ✗ NOT FEASIBLE | CLSTM requires time-ordered sequences per machine showing degradation; dataset lacks timestamps, machine IDs, and temporal ordering | Replace with XGBoost Regression on Tool Wear (0-254 min range) as analytical RUL proxy; document CLSTM as Phase 2 requirement contingent on longitudinal data collection |
| FR-7: Asset Health Gauge | ◐ PARTIALLY FEASIBLE | Can compute health from failure probability; "real-time" updates impossible with snapshot data | Reframe as "Current Health Status Indicator"; clarify that updates require new sensor snapshot input (not continuous) |
| FR-8: Predictive Alerts | ◐ PARTIALLY FEASIBLE | Threshold-based alerts feasible (e.g., trigger when failure_prob > 0.7); state-change detection requires temporal data | Implement threshold-based alerts; document that "state change detection" requires Phase 2 time-series architecture |
| FR-9: SHAP Explainability | ✓ FEASIBLE | SHAP library fully compatible with XGBoost on cross-sectional data; enables both global (feature importance) and local (per-prediction) explanations | Proceed as planned; include in dashboard and model reports |
| FR-10: Financial Impact Tracker | ✗ NOT FEASIBLE | Dataset contains only sensor readings and failure flags; zero financial/operational data (downtime logs, revenue per unit, maintenance costs) | Create placeholder UI component with calculation template; mark "Demo Only – Future Enhancement" until maintenance logs and business data available for integration |
| NFR-1: Performance (Near Real-Time) | ✓ FEASIBLE | XGBoost inference: <100ms; SHAP: <500ms; acceptable for batch processing and dashboard response | Proceed; validate inference time in prototype deployment; acceptable for non-critical alerting |
| NFR-2: Usability (Intuitive Interface) | ✓ FEASIBLE | SHAP visualizations and gauges are interpretable to non-technical users; no data limitation | Proceed with user-centric design; prototype with target user feedback |
| NFR-3: Reliability (High Recall) | ✓ FEASIBLE | XGBoost supports class weighting and custom loss functions; sufficient positive examples (339 failures) for recall optimization | Proceed; tune model hyperparameters targeting Recall ≥ 0.95; implement stratified cross-validation |

---

## Count Summary

- **✓ FEASIBLE:** 6 requirements (FR-1, FR-3, FR-5, FR-9, NFR-1, NFR-2, NFR-3 = 7 total)
- **◐ PARTIALLY FEASIBLE:** 3 requirements (FR-2, FR-7, FR-8) – require reframing or deferral of temporal aspects
- **✗ NOT FEASIBLE:** 4 requirements (FR-4, FR-6, FR-10 + NFR partial) – require data not in current dataset or architectural redesign

---

## Prototype Scope Impact

**Prototype is viable for:**
- Batch-mode failure classification with multi-class output (5 failure modes)
- Component wear estimation (analytical RUL from Tool Wear proxy)
- SHAP-based prediction explanations
- Threshold-based alerting
- Cross-sectional anomaly detection

**Prototype is NOT suitable for:**
- Real-time continuous monitoring (requires timestamps + streaming architecture)
- Temporal trend analysis (thermal trends, degradation slopes require sequences)
- LSTM/CLSTM prognosis (requires multi-step degradation profiles)
- Financial impact calculations (requires business data integration)

---

## Critical Dataset Constraints

| Constraint | Impact | Workaround |
| --- | --- | --- |
| **No timestamps** | Cannot construct time-series per machine | Use snapshot-based models (XGBoost); reframe temporal requirements |
| **No machine identifiers** | Cannot track degradation within machine units | Use cross-sectional analysis; treat each row as independent observation |
| **No sequence information** | LSTM/CLSTM impossible | Use analytical RUL (regression on Tool Wear feature) |
| **No business data** | Cannot calculate financial impact | Create placeholder component; defer to Phase 2 |
| **Static snapshot (10k rows)** | Limited to population-level patterns | Sufficient for prototype classification; production requires longitudinal data |

---

## Decision Rationale Summary

**Why the static snapshot is appropriate for prototype:**
- Demonstrates ML pipeline feasibility (data prep → feature engineering → classification → interpretation)
- Validates failure mode separability and feature engineering hypotheses
- Provides proof-of-concept for dashboard UI and SHAP explanations
- Identifies clear requirements for production Phase 2 (temporal data collection)

**Why temporal models are out-of-scope:**
- Cannot construct time-series without sequential observations per machine
- LSTM/CLSTM requires minimum 20-50 timesteps per unit for meaningful training
- Current data: ~1.5 observations per machine on average (10,000 rows ÷ ~6500 unique Product_IDs)
- Mathematical impossibility, not engineering choice

