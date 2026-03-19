# Software Requirements Specification (SRS) for IndustriSense-AI

## 1. Introduction

### 1.1 Purpose
This document provides a detailed description of the requirements for the IndustriSense-AI project. Its purpose is to define the scope, functionalities, and constraints of the system, serving as a foundational agreement between stakeholders on what the system should do. This project aims to develop a high-level prototype for a predictive maintenance solution, initially tailored for the tea processing industry, with the potential for broader industrial applications.

### 1.2 Project Scope
The project focuses on developing a predictive maintenance platform that analyzes sensor data from industrial machinery to predict failures and estimate the Remaining Useful Life (RUL) of components. The initial application is targeted at the Kenya Tea Development Agency (KTDA), focusing on critical assets like CTC (Crush, Tear, Curl) machines and withering fans. The system will use the public "AI4I 2020 Predictive Maintenance Dataset" as a synthetic baseline for model development. The final deliverable will be a functional prototype demonstrating the core problem-solving capabilities, including a decision-support dashboard.

### 1.3 Definitions, Acronyms, and Abbreviations
- **AI:** Artificial Intelligence
- **CLSTM:** Convolutional Long Short-Term Memory
- **CTC:** Crush, Tear, Curl (A type of tea processing machine)
- **KTDA:** Kenya Tea Development Agency
- **ML:** Machine Learning
- **MTBF:** Mean Time Between Failures
- **OEE:** Overall Equipment Effectiveness
- **PdM:** Predictive Maintenance
- **RUL:** Remaining Useful Life
- **SRS:** Software Requirements Specification
- **XAI:** Explainable AI
- **XGBoost:** Extreme Gradient Boosting

### 1.4 References
- Predictive Maintenance for KTDA: A Machine Learning Approach to Optimize Tea Processing Efficiency.pdf

### 1.5 Document Overview
This document is organized into three main sections. Section 1 provides an introduction and overview of the project. Section 2 gives an overall description of the product, its users, constraints, and assumptions. Section 3 details the specific requirements, including functional, non-functional, and interface requirements.

---

## 2. Overall Description

### 2.1 Product Perspective
IndustriSense-AI is a new, standalone product. It is conceived as an innovative, high-level prototype with no current investment. It serves to demonstrate a proof-of-concept for data-driven predictive maintenance in an industrial setting, using publicly available data to simulate a real-world scenario.

### 2.2 Product Functions
The primary functions of the system are:
1.  **Data Ingestion and Processing:** Ingest and clean machine sensor data.
2.  **Anomaly Detection:** Identify anomalies and potential sensor faults in the data stream.
3.  **Failure Classification:** Classify potential machine failure modes based on sensor patterns.
4.  **RUL Prognosis:** Forecast the remaining useful life of critical machine components.
5.  **Decision Support:** Present insights, alerts, and justifications through a user-friendly dashboard.

### 2.3 User Characteristics
The primary users of the system are:
-   **Factory Managers:** Oversee factory operations and use the dashboard to make strategic decisions about maintenance scheduling and resource allocation to minimize downtime and costs.
-   **Regional Engineers:** Monitor equipment health across multiple sites and use the system to diagnose issues and plan technical interventions.

### 2.4 Constraints
-   **Budget:** This is a zero-investment project. All development must use open-source technologies.
-   **Data:** The project will use the "AI4I 2020 Predictive Maintenance dataset" as a substitute for real proprietary data. The models will be built and validated on this synthetic data.
-   **Timescale:** As a prototype, the focus is on demonstrating core functionality rather than building a production-ready, scalable system.

### 2.5 Assumptions and Dependencies
-   The "AI4I 2020" dataset's parameters (RPM, Torque, Temperature, Tool Wear) are assumed to be reasonable proxies for the mechanical and thermal stresses experienced by tea processing equipment.
-   For a real-world deployment (beyond the prototype), it is assumed that reliable internet connectivity (e.g., 4G/5G) would be available at factory locations for data transmission.
-   It is assumed that existing maintenance logs and PLC data would be accessible for initial model training in a real-world scenario.

### 2.6 Critical Data Limitations (AUDIT ADDITION)

The IndustriSense-AI prototype is **fundamentally constrained by the nature of the dataset**: the AI4I 2020 dataset is a **static cross-sectional snapshot** with no temporal dimension.

**Dataset Characteristics:**
- **10,000 rows**, each representing a single observation/measurement snapshot
- **No timestamps, sequence IDs, or machine identifiers** that would enable time-series reconstruction
- **Cross-sectional data only**: Each row is independent; no longitudinal degradation profiles per machine

**Implications for System Capabilities:**
1. **Time-Series Models (e.g., CLSTM) are not applicable.** Temporal RUL prognosis requires sequential data showing component degradation over time for the same machine.
2. **Real-time monitoring is not possible.** The system can only provide snapshot-based predictions, not continuous state tracking or drift detection.
3. **Thermal Trend calculation is impossible.** Computing the slope of temperature over time requires time-indexed observations for each machine.
4. **RUL estimation must be analytical (cross-sectional)** rather than predictive (time-series based). Tool Wear (0-254 min) is used as a proxy for component degradation within a static context.

**Prototype Scope Consequence:**
- The system is suitable for **batch analysis of snapshot sensor data** (e.g., "Given today's sensor readings, what is the failure risk?")
- The system is **not suitable for continuous predictive monitoring** or temporal trend detection without architectural and data collection changes.

---

## 3. Specific Requirements

### 3.1 Requirements Feasibility Summary

| Requirement | Status | Basis |
|-------------|--------|-------|
| FR-1: Data Mapping | ✓ FEASIBLE | All required features present in dataset |
| FR-2: Anomaly Detection | ✓ FEASIBLE | Cross-sectional outlier detection via Isolation Forest |
| FR-3: Stress Index | ✓ FEASIBLE | Engineered feature shows strong OSF discrimination |
| FR-4: Thermal Differential | ✓ FEASIBLE (MODIFIED) | Snapshot thermal stress proxy (not trend slope) |
| FR-5: XGBoost Classification | ✓ FEASIBLE | Data supports multi-class failure mode classification |
| FR-6: RUL Estimation | ✓ FEASIBLE (MODIFIED) | Analytical regression on Tool Wear (not CLSTM forecasting) |
| FR-7: Health Gauge | ✓ FEASIBLE | Snapshot health score from failure probability |
| FR-8: Risk Alerts | ✓ FEASIBLE | Probability thresholds trigger alerts |
| FR-9: Statistical Explanations | ✓ FEASIBLE | Cross-sectional explanations fully supported |
| FR-10: Financial Tracking | ✗ FUTURE | Requires business data (Phase 2) |

### 3.1 Functional Requirements

#### 3.1.1 Data Processing and Feature Engineering

-   **FR-1 [FEASIBLE]:** The system shall map features from the source dataset to represent key physical processes (e.g., map "Torque" and "Rotational Speed" to CTC roller speed differential).
    - **Evidence:** Dataset contains exactly the features specified: Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min]. EDA confirms sensor data distributions are reasonable.

-   **FR-2 [PARTIALLY FEASIBLE]:** The system shall implement an Isolation Forest algorithm to detect sensor soft faults (e.g., drift, spikes).
    - **Evidence:** Dataset has no missing values or duplicates. However, being a static snapshot with single observations per product, anomaly detection is limited to cross-sectional outliers, not temporal drift detection.
    - **Proposed Way Forward:** Reframe FR-2 as "Cross-sectional anomaly detection" rather than temporal drift detection. Isolation Forest can detect unusual sensor combinations or extreme values within the snapshot, but cannot detect gradual drift or spikes across time.

-   **FR-3 [FEASIBLE]:** The system shall calculate a custom "Stress Index" feature, defined as `Torque * Tool Wear`, to predict overstrain failures.
    - **Evidence:** EDA demonstrates that Stress Index successfully differentiates Overstrain Failure (OSF) cases: Mean Stress Index for OSF=1 is 12,067 vs. OSF=0 is 4,238. Feature engineering is applicable.

-   **FR-4 [MODIFIED - TEMPERATURE DIFFERENTIAL]:** The system shall calculate a "Temperature Differential" feature defined as `Process temperature [K] - Air temperature [K]` to detect overheating or inadequate cooling.
    - **Evidence:** Dataset is a static cross-sectional snapshot preventing calculation of thermal *trend* (slope over time). However, Temperature Differential captures instantaneous thermal stress state. EDA confirms discriminative power: Mean Temp Differential for HDF=1 is 10.16 K vs. HDF=0 is 9.97 K. Statistical test shows p-value < 0.05, confirming association with heat dissipation failures.
    - **Implementation:**
      - Temperature Differential = `process_temperature - air_temperature`
      - Feature engineering pipeline will include this in model training
      - Dashboard will display current thermal stress level alongside temperature values
      - **Limitation (Documented):** Captures snapshot thermal state, not degradation *rate*. Time-series thermal trend slope requires longitudinal data (future enhancement)

#### 3.1.2 Machine Learning Models

-   **FR-5 [FEASIBLE]:** The system shall use an XGBoost model to classify machine failure modes. This model will be optimized for the F-beta score (with beta > 1) to prioritize Recall, minimizing the risk of missed failures.
    - **Evidence:** Dataset contains all failure mode flags (TWF, HDF, PWF, OSF, RNF) and diverse sensor features. EDA shows failure modes are distinguishable: OSF has Mean Stress Index of 12,067 vs. 4,238 for no failure. XGBoost is applicable to this cross-sectional classification task.

-   **FR-6 [MODIFIED - ANALYTICAL RUL ESTIMATION]:** The system shall use XGBoost regression to estimate the Remaining Useful Life (RUL) of critical components using Tool Wear as a proxy measurement.
    - **Evidence:** CLSTM requires sequential/temporal data (sensor readings ordered by time per machine). The dataset is a static snapshot with no time-series information. However, Tool Wear (range 0-254 minutes) directly measures component degradation and can be predicted analytically. EDA confirms Tool Wear is a strong discriminator across failure modes.
    - **Implementation:**
      - Model: XGBoost Regressor trained to predict Tool Wear (0-254 min) from sensor features
      - Interpretation: "Estimated remaining component wear = 254 - predicted_tool_wear [minutes]"
      - This provides analytical RUL estimation suitable for snapshot sensor data (not predictive time-series forecasting)
      - Dashboard will display current wear state and estimated remaining time before tool must be replaced
      - **Limitation (Documented):** Provides instantaneous wear estimate, not trend forecasting. Temporal RUL prognosis (predicting future degradation trajectory) requires longitudinal data (future enhancement with CLSTM)

#### 3.1.3 Decision-Support Dashboard

-   **FR-7 [FEASIBLE - BATCH MODE]:** The dashboard shall display a "Gauge-style" visual indicating the current health percentage of each analyzed asset.
    - **Implementation:** For a batch-submitted sensor snapshot, compute health score as: `Health % = (1 - failure_probability) × 100`
    - **Feasibility:** XGBoost model produces failure probability (0-1) for each prediction. Anomaly score from Isolation Forest can be incorporated to adjust health score.
    - **Visualization:** Gauge shows 0-100%, color-coded: Green (>80%), Yellow (50-80%), Red (<50%)
    - **Data Source:** Current snapshot analysis, not real-time streaming
    - **Limitation:** Shows snapshot health state at moment of analysis. Does not track health changes over time without resubmitting new sensor readings.

-   **FR-8 [FEASIBLE - PROBABILITY-BASED]:** The system shall generate alerts when a machine's predicted failure probability exceeds a configured threshold.
    - **Implementation:** Alert when `failure_probability > threshold` (default threshold = 0.7 = 70%)
    - **Alert Content:** "HIGH RISK: Failure probability = 85%. Recommended actions: Schedule maintenance within X hours."
    - **Feasibility:** XGBoost classification provides failure probability for each snapshot
    - **Failure Mode Alerts:** Separate alerts for each failure mode (TWF, HDF, PWF, OSF, RNF) with specific guidance
    - **Limitation:** Detects high-risk snapshots, not temporal transitions (e.g., "risk jumped from 20% to 80%"). Transition detection requires time-series comparison.

-   **FR-9 [FEASIBLE]:** The dashboard shall include transparency reports for each alert, showing which features most influenced the risk assessment through statistical variance analysis.
    - **Implementation:** For each prediction, generate a report showing top 3-5 sensors driving the failure probability.
    - **Example Output:** "Failure risk is HIGH because: (1) Torque is 20% above historical mean, (2) Tool Wear is 80% of max."
    - **Feasibility:** Statistical variance analysis is highly efficient for XGBoost on cross-sectional data.
    - **User Value:** Non-technical operators understand not just "risk = 85%" but WHY.

-   **FR-10 [FUTURE ENHANCEMENT - DATA REQUIRED]:** Future version shall feature a "Financial Impact Tracker" estimating prevented downtime and associated savings.
    - **Requirements for Implementation:** 
      - Historical maintenance logs with duration and date/time
      - Production revenue or cost per hour of downtime
      - Machine identification and asset values
      - Maintenance cost data
    - **Status:** Prototype cannot implement without business data. Placeholder UI provided showing expected calculation: `Annual_Savings = (predicted_failures_caught × cost_per_failure) - (false_alarms × investigation_cost)`
    - **Phase 2:** Implement when KTDA provides maintenance/financial data

### 3.2 Non-Functional Requirements

-   **NFR-1 (Performance):** Model inference for failure classification and RUL estimation should be completed quickly (< 1 second per prediction) to support batch analysis of sensor snapshots. The dashboard should load analysis results promptly. **Note:** This is snapshot-mode performance, not real-time continuous monitoring. Real-time monitoring with continuous state change detection is a future enhancement requiring longitudinal data collection.
-   **NFR-2 (Usability):** The dashboard interface must be intuitive and easily interpretable by non-technical users like factory managers.
-   **NFR-3 (Reliability):** The system's predictions, especially failure alerts, must be reliable. The model performance will be measured by prioritizing high Recall, as a false negative (missed failure) is significantly more costly than a false positive.

## 4. Prototype Scope, Capabilities, and Limitations

### 4.1 What the System CAN Do

**✓ Batch-Mode Snapshot Analysis**
- Ingest a single sensor reading (or batch of readings) from a machine
- Classify failure probability and predict which failure mode(s) are most likely
- Estimate remaining tool wear/useful life from sensor patterns
- Flag anomalous sensor combinations that warrant manual inspection
- Generate SHAP-based explanations for each prediction (why is this machine at risk?)
- Provide a health status indicator (0-100% operational health)
- Generate alerts when failure probability exceeds a configurable threshold

**✓ Class Imbalance Handling**
- Use weighted XGBoost training to address 3.4% failure rate in data
- Achieve high Recall (catch most actual failures) with stratified cross-validation

**✓ Interpretability**
- Feature importance analysis showing which sensors drive each prediction
- SHAP force plots for individual machine explanations
- Clear documentation of model assumptions and limitations

### 4.2 What the System CANNOT Do (Data Limitations)

**✗ Real-Time Continuous Monitoring**
- System requires static sensor snapshots; it cannot detect ongoing changes
- No integration with live sensor streams or IoT platforms
- Future enhancement requires: timestamps, continuous data logging, telemetry infrastructure

**✗ Temporal Trend Detection**
- Cannot detect rising temperature/wear trends that precede failures
- Cannot compute thermal slope, acceleration of wear, or other rate-of-change metrics
- Reason: Dataset lacks timestamps and sequence information per machine
- Future enhancement requires: weeks/months of operational data per equipment unit

**✗ Time-Series Predictive Models (e.g., CLSTM)**
- Cannot train deep learning models that learn degradation trajectories over time
- Cannot forecast "Machine will fail in N days based on current degradation rate"
- Reason: No sequential data (sensor readings ordered by time per machine)
- Future enhancement requires: at least 20-50 consecutive observations per machine unit

**✗ Financial Impact Tracking**
- Cannot estimate prevented downtime or associated cost savings
- Would require: maintenance logs, repair costs, production revenue, scheduling data
- Future enhancement when business data becomes available

**✗ Real-Time State Change Alerts**
- Cannot generate alerts like "Risk jumped from 20% to 80% - investigate now"
- Can only generate alerts on current snapshot probability (e.g., "Current risk is 85%")
- Reason: No temporal sequence to detect transitions

### 4.3 Appropriate Use Cases for This Prototype

1. **Maintenance Planning:** Batch analysis of multiple machines to prioritize maintenance schedules
2. **Operator Decision Support:** When a technician wants to understand why a specific sensor reading is concerning
3. **Model Baseline:** Establish classification accuracy baseline before deploying real-time monitoring
4. **Proof of Concept:** Demonstrate value of ML-driven maintenance to stakeholders with synthetic data

### 4.4 Transition to Production (Phase 2 Requirements)

To evolve from prototype to production-grade system:

**Infrastructure Changes**
- Deploy time-series database (InfluxDB, Prometheus) for continuous sensor logging
- Add timestamps and machine identifiers to all data
- Integrate with real-time data streams from factory sensors/PLCs

**Data Collection**
- Collect at least 3-6 months of sensor readings per equipment unit
- Log maintenance events with precise timing and outcomes
- Record production schedules, downtime, and costs

**Model Evolution**
- Retrain classification models on longitudinal data with temporal features
- Implement CLSTM networks for true RUL forecasting
- Add drift detection to alert when model predictions become unreliable

**Operational Integration**
- Deploy dashboard as real-time monitoring system
- Implement threshold tuning based on operational feedback
- Establish model retraining schedule (quarterly or on drift detection)

### 3.3 External Interface Requirements

#### 3.3.1 User Interfaces
-   The primary user interface will be a web-based dashboard. It must be responsive and accessible on standard web browsers. The dashboard will contain visualizations, alerts, and explanatory text as described in the functional requirements.

#### 3.3.2 Software Interfaces
-   The system will be developed using Python and standard data science libraries (e.g., Pandas, Scikit-learn, XGBoost, TensorFlow/Keras).
-   The dashboard may be built using a web framework like Flask/Django with a plotting library (e.g., Plotly, Dash) or a BI tool like Power BI capable of integrating Python visuals.
