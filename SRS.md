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

### 3.1 Functional Requirements

#### 3.1.1 Data Processing and Feature Engineering

-   **FR-1 [FEASIBLE]:** The system shall map features from the source dataset to represent key physical processes (e.g., map "Torque" and "Rotational Speed" to CTC roller speed differential).
    - **Evidence:** Dataset contains exactly the features specified: Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min]. EDA confirms sensor data distributions are reasonable.

-   **FR-2 [PARTIALLY FEASIBLE]:** The system shall implement an Isolation Forest algorithm to detect sensor soft faults (e.g., drift, spikes).
    - **Evidence:** Dataset has no missing values or duplicates. However, being a static snapshot with single observations per product, anomaly detection is limited to cross-sectional outliers, not temporal drift detection.
    - **Proposed Way Forward:** Reframe FR-2 as "Cross-sectional anomaly detection" rather than temporal drift detection. Isolation Forest can detect unusual sensor combinations or extreme values within the snapshot, but cannot detect gradual drift or spikes across time.

-   **FR-3 [FEASIBLE]:** The system shall calculate a custom "Stress Index" feature, defined as `Torque * Tool Wear`, to predict overstrain failures.
    - **Evidence:** EDA demonstrates that Stress Index successfully differentiates Overstrain Failure (OSF) cases: Mean Stress Index for OSF=1 is 12,067 vs. OSF=0 is 4,238. Feature engineering is applicable.

-   **FR-4 [NOT FEASIBLE]:** The system shall calculate a "Thermal Trend" feature by computing the slope of bearing temperature over time to detect overheating or lubrication issues.
    - **Evidence:** Dataset is a static cross-sectional snapshot with no timestamps or machine identifiers enabling time-series construction. EDA explicitly notes: "With this snapshot dataset, we cannot directly calculate a time-based slope for each machine."
    - **Proposed Way Forward:**
      - **Option A (Recommended):** Replace "Thermal Trend" with a "Temperature Differential" feature: `Process temperature [K] - Air temperature [K]`. EDA shows Mean Temp Diff for HDF=1 is 10.16 K vs. HDF=0 is 9.97 K, indicating some discriminative power.
      - **Option B:** Acknowledge FR-4 as out-of-scope for prototype, document as future requirement requiring real-time time-series data collection.

#### 3.1.2 Machine Learning Models

-   **FR-5 [FEASIBLE]:** The system shall use an XGBoost model to classify machine failure modes. This model will be optimized for the F-beta score (with beta > 1) to prioritize Recall, minimizing the risk of missed failures.
    - **Evidence:** Dataset contains all failure mode flags (TWF, HDF, PWF, OSF, RNF) and diverse sensor features. EDA shows failure modes are distinguishable: OSF has Mean Stress Index of 12,067 vs. 4,238 for no failure. XGBoost is applicable to this cross-sectional classification task.

-   **FR-6 [NOT FEASIBLE AS SPECIFIED]:** The system shall use a Convolutional LSTM (CLSTM) network to forecast the Remaining Useful Life (RUL) of critical components (e.g., rollers).
    - **Evidence:** CLSTM requires sequential/temporal data (e.g., sensor readings ordered by time for each machine). The dataset is a static snapshot with one row per (machine, observation) pair, containing no time-series or sequence information. EDA summary states: "Tool wear is a strong candidate for RUL prognosis, as it directly measures component degradation over time," but the dataset does not contain sequential degradation profiles.
    - **Proposed Way Forward:**
      - **Option A (Recommended - Analytical RUL):** Replace CLSTM with statistical regression models (e.g., XGBoost regression or linear regression) to predict Tool Wear as a proxy for RUL. Tool Wear ranges 0-254 minutes in the dataset, providing a quantifiable proxy. Reframe as "RUL Estimation" (analytical) rather than "RUL Prognosis" (predictive time-series).
      - **Option B (Future Enhancement):** Document CLSTM as a future requirement contingent on collecting longitudinal time-series data (e.g., sensor readings logged at regular intervals for each machine unit over its operational lifetime).

#### 3.1.3 Decision-Support Dashboard

-   **FR-7 [PARTIALLY FEASIBLE]:** The dashboard shall display a "Gauge-style" visual indicating the real-time health percentage of each monitored asset line.
    - **Evidence:** Dataset contains sufficient features to compute a health score (e.g., combining failure probability from XGBoost model with sensor anomaly scores). However, "real-time" is not achievable with static snapshot data.
    - **Proposed Way Forward:** Reframe as "Current Health Status Indicator" rather than "Real-time." Display health scores computed from the snapshot data and XGBoost predictions. Implement real-time monitoring as a future enhancement.

-   **FR-8 [PARTIALLY FEASIBLE]:** The system shall generate automated alerts (simulated as on-screen notifications) when a machine enters a high-risk failure state.
    - **Evidence:** XGBoost model can predict failure probability. Alerts can be generated for high-probability cases. However, the dataset provides snapshot probabilities, not state transitions over time.
    - **Proposed Way Forward:** Generate alerts based on current failure probability thresholds (e.g., "Failure probability > 70%"). Document that temporal state change detection (e.g., "risk increased from 20% to 80%") requires longitudinal data.

-   **FR-9 [FEASIBLE]:** The dashboard shall include a component that provides SHAP-based explanations for why an alert was triggered (e.g., "High vibration detected, likely due to bearing fatigue").
    - **Evidence:** SHAP explanations are applicable to XGBoost models on cross-sectional data. Can generate feature importance scores and local explanations for individual predictions.

-   **FR-10 [NOT FEASIBLE]:** The dashboard shall feature a "Financial Impact Tracker" that shows estimated savings from avoided downtime. This will be calculated by `avoided_downtime_hours * revenue_per_unit_of_tea`.
    - **Evidence:** Dataset contains no downtime data, revenue information, or maintenance cost data. SRS assumptions state "existing maintenance logs... would be accessible for initial model training in a real-world scenario," but these are not present in the prototype dataset.
    - **Proposed Way Forward:** Defer FR-10 as "Future Enhancement - Requires Business Data Integration." For prototype, provide a placeholder component showing the calculation template and expected inputs (downtime hours, revenue per unit) without actual values.

### 3.2 Non-Functional Requirements

-   **NFR-1 (Performance):** Model inference for failure classification and RUL should be completed in near real-time to provide timely alerts. The dashboard should load and update without noticeable lag.
-   **NFR-2 (Usability):** The dashboard interface must be intuitive and easily interpretable by non-technical users like factory managers.
-   **NFR-3 (Reliability):** The system's predictions, especially failure alerts, must be reliable. The model performance will be measured by prioritizing high Recall, as a false negative (missed failure) is significantly more costly than a false positive.

### 3.3 External Interface Requirements

#### 3.3.1 User Interfaces
-   The primary user interface will be a web-based dashboard. It must be responsive and accessible on standard web browsers. The dashboard will contain visualizations, alerts, and explanatory text as described in the functional requirements.

#### 3.3.2 Software Interfaces
-   The system will be developed using Python and standard data science libraries (e.g., Pandas, Scikit-learn, XGBoost, TensorFlow/Keras).
-   The dashboard may be built using a web framework like Flask/Django with a plotting library (e.g., Plotly, Dash) or a BI tool like Power BI capable of integrating Python visuals.
