# Software Requirements Specification (SRS) for IndustriSense AI

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for **IndustriSense AI**, an advanced predictive maintenance SaaS platform. Initially conceived for the tea processing industry (KTDA), the system has evolved into a generalized industrial intelligence solution. Its primary goal is to empower factory stakeholders to move from reactive maintenance to an ROI-driven proactive model using machine learning and explainable AI (XAI).

### 1.2 Project Scope
IndustriSense AI provides a full-stack SaaS environment that ingest sensor telemetry to predict equipment failure and estimate Remaining Useful Life (RUL). The scope includes:
- **Core ML Engine:** Dual XGBoost cores for high-recall failure classification and analytical RUL estimation.
- **SaaS Infrastructure:** Secure multi-tenant architecture with user authentication and fleet isolation.
- **Fintech Integration:** Automated M-Pesa payment processing via PayHero for industrial licensing.
- **Decision Support:** A professional, responsive dashboard featuring health gauges, diagnostic reports, and an AI Fleet Assistant.

### 1.3 Definitions, Acronyms, and Abbreviations
- **CTC:** Crush, Tear, Curl (Core tea processing machinery).
- **KTDA:** Kenya Tea Development Agency.
- **RUL:** Remaining Useful Life (Operating minutes remaining before critical wear).
- **STK Push:** SIM Toolkit Push (Automated M-Pesa prompt).
- **XAI:** Explainable AI (Features that justify model decisions).
- **SaaS:** Software as a Service.

### 1.4 References
- PayHero Kenya API Documentation.
- AI4I 2020 Predictive Maintenance Dataset (UCI Machine Learning Repository).
- IndustriSense AI Internal Architecture Guide.

---

## 2. Overall Description

### 2.1 Product Perspective
IndustriSense AI is a standalone SaaS platform designed for industrial commercialization. It bridges the gap between raw PLC/SCADA telemetry and executive-level ROI, providing a specialized interface for both maintenance engineers and factory managers.

### 2.2 Product Functions
1.  **Multi-Tenant Fleet Management:** Securely isolate equipment data per organization.
2.  **Failure Forecaster:** Predict 5 distinct failure modes (TWF, HDF, PWF, OSF, RNF).
3.  **Analytical RUL Estimation:** Calculate remaining operating minutes based on cumulative wear patterns.
4.  **Industrial Licensing:** Automated tiered subscription management ($299 - $1,999/mo).
5.  **Diagnostic Transparency:** Provide SHAP-based justifications for every failure alert.

### 2.3 User Characteristics
-   **Factory Managers:** Focus on ROI, uptime metrics, and financial impact.
-   **Maintenance Engineers:** Focus on specific sensor telemetry, RUL, and diagnostic guidance.
-   **IoT Administrators:** Focus on system connectivity and API integrations.

### 2.4 Constraints & Assumptions
-   **Data Nature:** Models are optimized for the AI4I 2020 cross-sectional dataset; real-time trend detection requires future longitudinal data.
-   **Connectivity:** High-availability STK Push depends on the user's mobile network and the PayHero gateway status.
-   **Local Development:** Callback URLs for local testing require a tunnel (e.g., Ngrok) to receive PayHero server-to-server notifications.

---

## 3. Specific Requirements

### 3.1 Functional Requirements (FR)

| ID | Requirement | Status | Description |
|----|-------------|--------|-------------|
| **FR-1** | **Multi-Tenancy** | ✓ IMPLEMENTED | System securely isolates machines so users only see their assigned fleet. |
| **FR-2** | **XGBoost Classifier** | ✓ IMPLEMENTED | Dual-core engine optimized for high-recall failure detection. |
| **FR-3** | **RUL Regressor** | ✓ IMPLEMENTED | Analytical estimation of tool wear using sanitized telemetry. |
| **FR-4** | **PayHero Integration** | ✓ IMPLEMENTED | Automated STK Push and callback handling for M-Pesa payments. |
| **FR-5** | **Tiered Licensing** | ✓ IMPLEMENTED | Three industrial tiers: Operational Base, Production Pro, Industrial Nexus. |
| **FR-6** | **Explainable AI (XAI)** | ✓ IMPLEMENTED | Statistical variance reports showing top sensors driving risk. |
| **FR-7** | **Fleet Assistant** | ✓ IMPLEMENTED | Interactive Bot for on-page documentation and metric explanations. |
| **FR-8** | **Manual Diagnostics** | ✓ IMPLEMENTED | Web-based interface for processing ad-hoc sensor snapshots. |

#### 3.1.1 The Industrial Payment Lifecycle
- **STK Initiation:** System shall trigger an automated M-Pesa prompt upon plan selection.
- **Callback Handling:** System shall process server-to-server POST notifications from PayHero to confirm transactions.
- **Status Polling:** System shall implement a fallback polling mechanism to verify status if the callback is delayed.
- **Access Control:** System shall restrict features (e.g., RUL Forecasting, API Access) based on the user's active subscription level.

### 3.2 Non-Functional Requirements (NFR)

-   **NFR-1 (Security):** All passwords shall be hashed (PBKDF2); CSRF protection shall be active on all POST requests.
-   **NFR-2 (Reliability):** Failure classification shall prioritize Recall (min. 95% target) to ensure zero missed catastrophic events.
-   **NFR-3 (Usability):** The dashboard shall be fully responsive, supporting 4K monitors and mobile tablets for floor-walking engineers.
-   **NFR-4 (Performance):** Prediction results from the Dual-XGBoost engine must be returned within <500ms.

---

## 4. Platform Capabilities & Scope

### 4.1 What the System CAN Do
- **Proactive Risk Scoring:** Move from "Is it broken?" to "What is the probability it breaks today?".
- **Maintenance Prioritization:** Rank an entire fleet of 50+ machines by health criticality.
- **Secure Commercialization:** Manage the complete lifecycle from account registration to paid industrial licensing.
- **Diagnostic Justification:** Show operators the "Reason Code" (e.g., Torque/Speed interaction) for every alert.

### 4.2 Known Data Limitations
- **Snapshots only:** The system analyzes the "Current State" and does not yet account for "Rate of Change" (Longitudinal trends).
- **Environmental Context:** AI does not account for external factory ambient factors not present in the sensor stream.

---

## 5. System Architecture & Interfaces

### 5.1 Software Interfaces
- **Backend:** Flask 3.0 (Python 3.13), SQLAlchemy, Requests.
- **ML Layer:** XGBoost 3.2.0, Scikit-Learn, Pandas.
- **Payments:** PayHero V2 REST API (Basic Auth).
- **Frontend:** Bootstrap 5, FontAwesome 6, Vanilla JS (ES6+).

### 5.2 User Interfaces
- **Industrial Dashboard:** Real-time health tiles and stratified status counts.
- **Diagnostic Modal:** Deep-dive report including variance analysis and operator recommendations.
- **Billing Portal:** Value-based plan comparison and secure checkout.
