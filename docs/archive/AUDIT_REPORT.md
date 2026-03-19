# Technical Audit Report: IndustriSense-AI

**Audit Date:** January 9, 2026  
**Audit Scope:** Complete project review (dataset, EDA, SRS, README, source code structure)  
**Auditor Role:** Technical Validator - Evidence-Driven Assessment  

---

## Executive Summary

IndustriSense-AI is a **predictive maintenance prototype with correctly scoped batch-analysis capabilities** and **5 critical gaps between original SRS and dataset realities**. The dataset's static, cross-sectional nature fundamentally precludes temporal modeling (CLSTM, Thermal Trends, real-time monitoring). 

**Key Findings:**
- ✓ **6 requirements are FEASIBLE** (Failure Classification, Stress Index, SHAP Explanations, Feature Mapping, Feature Engineering foundation)
- ◐ **3 requirements are PARTIALLY FEASIBLE** (Anomaly Detection, Alerts, Health Dashboard—all require reframing from temporal to snapshot-based)
- ✗ **2 requirements are NOT FEASIBLE** (Thermal Trend calculation, CLSTM RUL Prognosis, Financial Impact Tracker)

**Updated documentation** (SRS.md and README.md) now includes feasibility labels and "Proposed Way Forward" sections with realistic alternatives.

---

## PART 1: DATASET & EDA VALIDATION

### Dataset Overview

| Attribute | Details |
|-----------|---------|
| **File(s)** | `ai4i2020.csv` (10,001 rows incl. header), `predictive_maintenance.csv` (duplicate, 10,001 rows) |
| **Observations** | 10,000 cross-sectional snapshots |
| **Temporal Structure** | NONE - No timestamps, no machine sequence IDs, no time indices |
| **Target Variable** | Machine failure (0/1), plus 5 specific failure modes (TWF, HDF, PWF, OSF, RNF) |
| **Features** | 8 sensor/operational features + metadata |
| **Data Quality** | 0 missing values, 0 duplicates (EDA-verified) |

### Feature Inventory

| Feature | Type | Range | EDA Finding |
|---------|------|-------|-------------|
| UDI | Identifier | 1-10000 | Unique row index |
| Product ID | Categorical | M14860-H29xxx | Machine model identifier (no sequence) |
| Type | Categorical | {M, L, H} | Product type, 3 classes |
| Air temperature [K] | Float | 295.3-304.5 | Mean 300.00 K, std 2.00 K |
| Process temperature [K] | Float | 305.7-313.8 | Mean 310.01 K, std 1.48 K |
| Rotational speed [rpm] | Int | 1168-2886 | Mean 1538.78 rpm, std 179.28 rpm |
| Torque [Nm] | Float | 3.8-76.6 | Mean 39.99 Nm, std 9.97 Nm |
| Tool wear [min] | Int | 0-254 | Mean 107.95 min, std 63.65 min |

### Failure Distribution (EDA Evidence)

| Failure Mode | Count | Pct | Notes |
|--------------|-------|-----|-------|
| Machine failure=0 | 9661 | 96.6% | Class imbalance: positive cases only 3.4% |
| Machine failure=1 | 339 | 3.4% | Total failures |
| TWF (Tool Wear Fail) | 95 | 0.95% | Rare failure mode |
| HDF (Heat Dissip Fail) | 114 | 1.14% | Low frequency |
| PWF (Power Fail) | 71 | 0.71% | Low frequency |
| OSF (Overstrain Fail) | 49 | 0.49% | Rarest mode |
| RNF (Random Fail) | 10 | 0.10% | Nearly absent |

### EDA Validation Against SRS

| EDA Section | Finding | SRS Alignment |
|-------------|---------|---------------|
| **Data Quality** | Zero missing/duplicates, clean for immediate use | ✓ Matches SRS assumption 2.5 |
| **Feature Distributions** | Reasonable ranges, align with physical machinery proxies | ✓ Supports FR-1 (feature mapping) |
| **Stress Index** | Mean 4,314.66; Strong OSF discriminator (OSF: 12,067 vs. no-OSF: 4,238) | ✓ Validates FR-3 |
| **Temperature Differential** | (Process - Air): HDF cases 10.16K vs. normal 9.97K | ✓ Supports FR-4 alternative |
| **Failure Mode Separation** | Different failure modes show distinct sensor profiles | ✓ XGBoost classification feasible (FR-5) |
| **Time-Series Readiness** | **NO TIMESTAMPS, NO SEQUENCE IDS** - snapshot data only | ✗ **BREAKS FR-4, FR-6** |

### Critical Limitation: No Temporal Structure

**Evidence from Dataset Structure:**
```
Row 1: UDI=1, Product_ID=M14860, Air_temp=298.1, ..., Tool_wear=0
Row 2: UDI=2, Product_ID=L47181, Air_temp=298.2, ..., Tool_wear=3
Row 3: UDI=3, Product_ID=L47182, Air_temp=298.1, ..., Tool_wear=5
...
Row 10000: UDI=10000, Product_ID=..., ..., Tool_wear=254
```

**No additional columns for:**
- Timestamp / datetime
- Machine unit ID or serial number
- Operational cycle number
- Maintenance history flags

**EDA Explicit Statement:**
> "The KTDA document suggests calculating a `Thermal Trend` (slope of bearing temperature over time). **With this snapshot dataset, we cannot directly calculate a time-based slope for each machine.** However, we can and will analyze the relationship between temperature, tool wear, and failures to find proxies for overheating issues."

**Conclusion:** The dataset **does not support CLSTM, time-series models, or temporal trend analysis**. RUL must be estimated analytically from static features.

---

## PART 2: REQUIREMENTS FEASIBILITY ASSESSMENT

### Functional Requirements (FR) - Detailed Assessment

#### FR-1: Feature Mapping ✓ FEASIBLE

**Requirement:**  
"The system shall map features from the source dataset to represent key physical processes (e.g., map 'Torque' and 'Rotational Speed' to CTC roller speed differential)."

**Evidence:**
- Dataset provides exact required fields: Rotational speed [rpm], Torque [Nm], Temperature sensors
- EDA confirms distributions are reasonable proxies for machinery stress
- Feature mapping is mathematical transformation, requires no temporal data

**Decision:** **FEASIBLE**

---

#### FR-2: Isolation Forest for Anomaly Detection ◐ PARTIALLY FEASIBLE

**Requirement:**  
"The system shall implement an Isolation Forest algorithm to detect sensor soft faults (e.g., drift, spikes)."

**Current Interpretation Gap:**  
- Original SRS implies temporal anomalies: "drift" suggests gradual sensor degradation over time; "spikes" suggest sudden anomalies within a time series
- Dataset structure: only cross-sectional outliers detectable

**Evidence:**
- Isolation Forest **can** detect extreme/unusual sensor combinations in the snapshot (e.g., unusually high torque + high temperature)
- Isolation Forest **cannot** detect drift (requires multiple readings from same machine over time) or spike patterns (requires temporal sequencing)

**Decision:** **PARTIALLY FEASIBLE**  
**Proposed Way Forward:**
- Reframe as "Cross-sectional Anomaly Detection" – detect unusual machines/readings relative to population distribution
- Drift/spike detection deferred to real-time monitoring phase requiring time-series data

---

#### FR-3: Stress Index Feature ✓ FEASIBLE

**Requirement:**  
"The system shall calculate a custom 'Stress Index' feature, defined as `Torque * Tool Wear`, to predict overstrain failures."

**Evidence (EDA Results):**

```
Stress Index = df['Torque [Nm]'] * df['Tool wear [min]']
Descriptive Statistics:
  Count: 10000
  Mean: 4314.66
  Std Dev: 2826.57
  Min: 0.0
  Max: 16497.0

Mean Stress Index by OSF Status:
  OSF=0 (No Overstrain): 4237.94
  OSF=1 (Overstrain):  12066.99
  
Difference: 2.85x higher for overstrain cases → Strong predictive signal
```

**Decision:** **FEASIBLE**

---

#### FR-4: Thermal Trend Feature ✗ NOT FEASIBLE

**Requirement:**  
"The system shall calculate a 'Thermal Trend' feature by computing the slope of bearing temperature over time to detect overheating or lubrication issues."

**Core Issue:**  
Slope = dT/dt requires two or more observations for the same machine at different times. Dataset has no timestamps and no machine-level identifiers enabling sequence reconstruction.

**Evidence:**
- Dataset: Single row per (machine, sensor_snapshot) pair
- Prerequisite unmet: "ordered by time for each machine" – impossible to construct

**EDA Explicit Statement:**
> "The KTDA document suggests calculating a `Thermal Trend` (slope of bearing temperature over time). **With this snapshot dataset, we cannot directly calculate a time-based slope for each machine.**"

**Decision:** **NOT FEASIBLE** (for prototype; future enhancement with real-time data)

**Proposed Way Forward:**
- **Option A (Recommended):** Replace with Temperature Differential feature: `Process temperature [K] - Air temperature [K]`
  - EDA shows Mean Temp Diff for HDF=1 is 10.16 K vs. HDF=0 is 9.97 K (valid discriminator)
  - Computable from snapshot data
  - Approximates overheating signal without requiring time-series

- **Option B:** Document as out-of-scope for prototype; require real-time time-series data collection in production

---

#### FR-5: XGBoost Failure Classification ✓ FEASIBLE

**Requirement:**  
"The system shall use an XGBoost model to classify machine failure modes. This model will be optimized for the F-beta score (with beta > 1) to prioritize Recall, minimizing the risk of missed failures."

**Evidence:**
- 10,000 labeled examples available across 6 failure classes (Machine failure + 5 modes)
- EDA shows failure modes are distinguishable by sensor profiles (different mean values across TWF, HDF, PWF, OSF, RNF)
- XGBoost is designed for cross-sectional classification
- Class imbalance (3.4% positive) is manageable with weighted loss functions

**Decision:** **FEASIBLE**

---

#### FR-6: CLSTM RUL Prognosis ✗ NOT FEASIBLE (as specified)

**Requirement:**  
"The system shall use a Convolutional LSTM (CLSTM) network to forecast the Remaining Useful Life (RUL) of critical components (e.g., rollers)."

**Core Issue:**  
CLSTM (Convolutional LSTM) is a deep learning architecture designed for sequential data: it processes time-series to predict future states. RUL prognosis from CLSTM means predicting "how much longer until failure" based on observed degradation trajectories.

**Dataset Limitation:**
- No degradation trajectories (no time-ordered observations per machine)
- Cannot construct sequences showing tool wear progression or thermal evolution

**Example of What's Needed (missing):**
```
Machine_ID | Timestamp | Tool_Wear | Temp | ... (time sequence for ONE machine)
001        | 2024-01-01 10:00 | 5 | 308.2
001        | 2024-01-01 11:00 | 7 | 308.5
001        | 2024-01-01 12:00 | 9 | 308.8
... degradation pattern over time ...
```

**What We Have:**
```
Row 1 | Product_ID=M14860 | Tool_wear=0
Row 2 | Product_ID=L47181 | Tool_wear=3
Row 3 | Product_ID=L47182 | Tool_wear=5
... (no time ordering, no machine-level tracking)
```

**EDA Assessment:**
> "Tool wear is a strong candidate for RUL prognosis, as it directly measures component degradation over time."

This refers to Tool wear as a **proxy variable** (wear measured in minutes), not as a time-series capable of training CLSTM.

**Decision:** **NOT FEASIBLE** (as specified)

**Proposed Way Forward:**
- **Option A (Recommended - Analytical RUL):**
  - Use regression models (XGBoost Regressor, Linear Regression) to predict Tool Wear (0-254 min) from sensor features
  - Interpret Tool Wear prediction as "estimated remaining component lifespan in minutes"
  - Reframe requirement as "RUL Estimation" (analytical) instead of "RUL Prognosis" (predictive)
  - Example: Model predicts "Tool Wear = 180 min" given current sensor state → interpret as "~180 min remaining until threshold"

- **Option B (Future Enhancement):**
  - Document CLSTM as a requirement for Phase 2
  - Prerequisite: Collect longitudinal data (sensor logs with timestamps and machine identifiers)
  - This enables construction of degradation sequences per machine

---

### Functional Requirements: Dashboard Features

#### FR-7: Asset Health Gauge ◐ PARTIALLY FEASIBLE

**Requirement:**  
"The dashboard shall display a 'Gauge-style' visual indicating the real-time health percentage of each monitored asset line."

**Issues:**
- "Real-time" implies continuous updating with fresh sensor data; snapshot data cannot provide this
- "Health percentage" is computable (e.g., 100% - failure_probability%)

**Evidence:**
- XGBoost provides failure probability (0-1) usable as inverse health metric
- Snapshot-based health is meaningful but static, not dynamic

**Decision:** **PARTIALLY FEASIBLE**

**Proposed Way Forward:**
- Reframe as "Current Health Status Indicator" (snapshot-based, not real-time)
- Display health score = (1 - failure_probability) × 100%
- Document limitation: "Updates require new sensor snapshot input; not continuous monitoring"

---

#### FR-8: Predictive Alerts ◐ PARTIALLY FEASIBLE

**Requirement:**  
"The system shall generate automated alerts (simulated as on-screen notifications) when a machine enters a high-risk failure state."

**Issues:**
- "State change" (e.g., "risk increased from 20% to 80%") requires two timestamped observations
- "High-risk failure state" is definable as threshold (e.g., failure_prob > 70%)

**Evidence:**
- XGBoost probability output enables threshold-based alerts
- Cannot detect state transitions without temporal data

**Decision:** **PARTIALLY FEASIBLE**

**Proposed Way Forward:**
- Generate alerts when failure_probability exceeds threshold (e.g., 0.7)
- Alert type: "Static-Threshold Alert" (this snapshot predicts high risk)
- Not: "State-Change Alert" (machine has deteriorated since last check) – requires time-series

---

#### FR-9: SHAP Explainability ✓ FEASIBLE

**Requirement:**  
"The dashboard shall include a component that provides SHAP-based explanations for why an alert was triggered (e.g., 'High vibration detected, likely due to bearing fatigue')."

**Evidence:**
- SHAP is model-agnostic and fully compatible with XGBoost on cross-sectional data
- Can generate both global (feature importance) and local (per-prediction) explanations

**Decision:** **FEASIBLE**

---

#### FR-10: Financial Impact Tracker ✗ NOT FEASIBLE

**Requirement:**  
"The dashboard shall feature a 'Financial Impact Tracker' that shows estimated savings from avoided downtime. This will be calculated by `avoided_downtime_hours * revenue_per_unit_of_tea`."

**Issues:**
1. **Dataset lacks downtime data:** No maintenance logs, no historical downtime durations
2. **Dataset lacks financial data:** No revenue per unit, no maintenance costs, no production schedules
3. **SRS Assumption Unfulfilled:** Section 2.5 states "existing maintenance logs... would be accessible for initial model training in a real-world scenario" – but prototype uses only synthetic AI4I data

**Evidence:**
- Dataset contains only sensor readings and failure flags
- No columns for: `downtime_hours`, `cost`, `revenue`, `maintenance_log_id`, etc.

**Decision:** **NOT FEASIBLE** (requires integration of business data not in prototype)

**Proposed Way Forward:**
- Create placeholder dashboard component showing calculation template:
  - Input fields: [Avoided_Downtime_Hours], [Revenue_per_Unit]
  - Display formula: Savings = input1 × input2
- Document as "Future Enhancement - Requires Business Data Integration"
- Mark component as "Demo Only" until real maintenance logs and financial data available

---

### Non-Functional Requirements (NFR) Status

#### NFR-1: Performance (Near Real-Time Inference) ✓ FEASIBLE

**Requirement:**  
"Model inference for failure classification and RUL should be completed in near real-time to provide timely alerts. The dashboard should load and update without noticeable lag."

**Evidence:**
- XGBoost inference: <100ms per prediction on standard hardware
- SHAP computation: <500ms per prediction (acceptable for batch)
- Dashboard rendering: Standard web frameworks (Dash, Flask) handle snapshots efficiently

**Decision:** **FEASIBLE** – with caveat that "real-time" means <1s response time to user input, not continuous background monitoring

---

#### NFR-2: Usability (Intuitive Interface) ✓ FEASIBLE

**Requirement:**  
"The dashboard interface must be intuitive and easily interpretable by non-technical users like factory managers."

**Evidence:**
- No technical blockers (design choice, not data-dependent)
- SHAP explanations improve interpretability

**Decision:** **FEASIBLE** – design responsibility

---

#### NFR-3: Reliability (High Recall) ✓ FEASIBLE

**Requirement:**  
"The system's predictions, especially failure alerts, must be reliable. The model performance will be measured by prioritizing high Recall, as a false negative (missed failure) is significantly more costly than a false positive."

**Evidence:**
- XGBoost supports custom loss functions and class weights for recall prioritization
- Dataset provides sufficient examples for model training (339 failures, 10000 total)

**Decision:** **FEASIBLE** – depends on model tuning and validation, not data limitation

---

## PART 3: EDA IMPROVEMENT SUGGESTIONS

### Gaps in Current EDA

The current EDA notebook (1_EDA.ipynb) covers data quality, feature distributions, and basic failure mode analysis well but lacks:

#### 1. **Class Imbalance Analysis**
- **Missing:** Detailed imbalance ratio assessment and impact on model training
- **Suggestion:** Add cells analyzing:
  - Imbalance ratio (96.6% negative, 3.4% positive)
  - Imbalance per failure mode (RNF: 0.1%, OSF: 0.49%, etc.)
  - Implications for XGBoost class weighting
  - Recommendation for stratified cross-validation

#### 2. **Feature Correlation & Multicollinearity**
- **Missing:** Correlation matrix, VIF (Variance Inflation Factor) analysis
- **Suggestion:** Add heatmap and VIF scores to detect multicollinearity between:
  - Air temp vs. Process temp (likely correlated)
  - Rotational speed vs. Torque
  - Tool wear vs. Stress Index

#### 3. **Failure Mode Co-occurrence Analysis**
- **Missing:** How often multiple failure modes occur together
- **Suggestion:** Add contingency tables/Venn diagrams showing overlap between TWF, HDF, PWF, OSF, RNF
- **Example Insight:** Are some machines prone to multiple failure modes simultaneously?

#### 4. **Model Feasibility Validation**
- **Missing:** Explicit assessment of dataset suitability for stated algorithms
- **Suggestion:** Add sections:
  - "CLSTM Feasibility Check" – why time-series models won't work (reinforce with data structure analysis)
  - "Thermal Trend Feasibility Check" – demonstrate impossibility with explicit code attempt
  - "RUL Proxy Validation" – confirm Tool Wear as viable proxy

#### 5. **Outlier/Anomaly Pattern Documentation**
- **Missing:** Characterization of unusual observations using Isolation Forest
- **Suggestion:** Apply Isolation Forest, analyze anomalous rows, determine if they correspond to rare failure modes or sensor errors

#### 6. **Feature Engineering Validation**
- **Missing:** Statistical tests for engineered features (Stress Index, Temp Diff)
- **Suggestion:** Add:
  - ANOVA F-tests: Stress Index vs. failure classes
  - T-tests: Temperature Differential between HDF vs. no-HDF
  - Effect sizes (Cohen's d)

#### 7. **Data Sufficiency Assessment**
- **Missing:** Power analysis / sample size check
- **Suggestion:** Estimate required sample size for desired model performance (Recall ≥ 0.95) given imbalance

---

## PART 4: FEASIBILITY SUMMARY TABLE

| Requirement ID | Requirement | Status | Evidence/Reason | Way Forward |
|---|---|---|---|---|
| FR-1 | Feature mapping to physical processes | ✓ FEASIBLE | Dataset contains exact required sensor features; EDA validates distributions | Proceed as planned |
| FR-2 | Isolation Forest anomaly detection | ◐ PARTIALLY | Can detect cross-sectional outliers; cannot detect temporal drift | Reframe as "cross-sectional anomaly detection"; defer drift to Phase 2 |
| FR-3 | Stress Index (Torque × Tool Wear) | ✓ FEASIBLE | EDA confirms strong OSF discrimination (2.85x difference) | Proceed; validate with statistical tests |
| FR-4 | Thermal Trend (slope over time) | ✗ NOT FEASIBLE | No timestamps/sequences in dataset; mathematically impossible | Replace with Temperature Differential; document as future enhancement |
| FR-5 | XGBoost failure classification | ✓ FEASIBLE | 10k labeled examples, distinguishable failure modes | Proceed; implement class weighting for imbalance handling |
| FR-6 | CLSTM RUL Prognosis | ✗ NOT FEASIBLE | CLSTM requires time-series; dataset is static snapshot | Use XGBoost Regressor on Tool Wear (analytical RUL estimation); CLSTM as Phase 2 requirement |
| FR-7 | Real-time Asset Health Gauge | ◐ PARTIALLY | Can compute health from failure probability; "real-time" not feasible | Reframe as "Current Health Status Indicator"; snapshot-based |
| FR-8 | Predictive Alerts | ◐ PARTIALLY | Threshold-based alerts feasible; state-change detection not | Generate alerts from failure probability thresholds; document temporal limitation |
| FR-9 | SHAP Explainability | ✓ FEASIBLE | SHAP fully compatible with XGBoost on cross-sectional data | Proceed as planned |
| FR-10 | Financial Impact Tracker | ✗ NOT FEASIBLE | No downtime/cost/revenue data in dataset | Create placeholder component; defer integration to Phase 2 |
| NFR-1 | Performance (near real-time) | ✓ FEASIBLE | XGBoost + SHAP inference <1s on standard hardware | Proceed; validate inference time in prototype |
| NFR-2 | Usability (intuitive interface) | ✓ FEASIBLE | SHAP explanations enhance interpretability; design choice | Proceed with user-centric design |
| NFR-3 | Reliability (high recall) | ✓ FEASIBLE | XGBoost supports class weighting and custom loss functions | Proceed; tune model for recall ≥ 0.95 |

---

## PART 5: CRITICAL SUMMARY FOR STAKEHOLDERS

### What the System CAN Do (Prototype Scope - FEASIBLE)

1. **Classify failure modes** from snapshot sensor data using XGBoost
2. **Estimate component wear (RUL proxy)** using regression on Tool Wear
3. **Explain predictions** using SHAP feature importance
4. **Detect outlier machines** using cross-sectional anomaly detection
5. **Compute health scores** as inverse failure probability
6. **Generate threshold-based alerts** ("High failure risk detected")

### What the System CANNOT Do Without Architectural Change (NOT FEASIBLE)

1. **Monitor machines continuously** over time – requires streaming/logged data with timestamps
2. **Detect thermal degradation trends** – requires time-series temperature observations
3. **Predict RUL using CLSTM** – requires degradation sequences per machine
4. **Calculate financial impact** – requires maintenance logs and business data
5. **Track health state changes** – requires multi-timestep observations

### Bridge to Production

To transition from prototype to production system:

| Gap | Current (Prototype) | Production Requirements |
|-----|---|---|
| **Data Frequency** | Snapshot (one-off) | Time-series (continuous/periodic logging) |
| **Machine Tracking** | Implicit (single analysis) | Explicit IDs + persistent storage for each machine |
| **Timestamps** | None | Required (enables sequence construction) |
| **Models** | XGBoost (cross-sectional) | LSTM/CLSTM (temporal sequence models) |
| **RUL Approach** | Analytical (wear proxy) | Predictive (degradation trajectory) |
| **Financial Data** | None | Downtime logs, costs, revenue per unit |

---

## AUDIT CONCLUSIONS

1. **SRS is realistic with amendments:** Original requirements can be reframed to align with dataset constraints.

2. **EDA validates key hypotheses:** Stress Index, Temperature Differential, and failure mode separation confirmed.

3. **Documentation updated:** SRS.md and README.md now include feasibility labels and "Proposed Way Forward" for each requirement.

4. **Prototype scope is appropriate:** Batch-analysis failure classification with SHAP explainability is achievable and valuable.

5. **Future vision is clear:** Transition path to temporal modeling (CLSTM) is documented contingent on real-time data collection.

**No data quality issues found.** Dataset is clean, suitable for immediate use for cross-sectional analysis.

---

## References

- **Dataset:** `data/raw/ai4i2020.csv` (10,000 observations)
- **EDA:** `notebooks/1_EDA.ipynb` (completed analysis)
- **SRS:** `SRS.md` (updated with feasibility assessments)
- **README:** `README.md` (updated with system limitations table)
- **Original Domain References:** Two PDF documents in project root (not fully parseable in audit)

---

**Audit Completed:** January 9, 2026  
**Status:** All required documentation updates complete  
**Action Required:** Review updated SRS and README for stakeholder approval
