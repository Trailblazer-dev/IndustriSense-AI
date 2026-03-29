# Test Plan: IndustriSense AI

## 1. Introduction

### 1.1 Purpose
This Test Plan defines the strategy, objectives, and scope for verifying the **IndustriSense AI** predictive maintenance platform. It ensures that the system meets the functional requirements defined in the SRS and the architectural standards in the SDD.

### 1.2 Test Items
- **Core ML Engine:** XGBoost Classifier and Regressor.
- **SaaS Backend:** Multi-tenant organization mapping and RBAC.
- **Fintech Layer:** PayHero M-Pesa STK Push and callback logic.
- **Human Interface:** Industrial Dashboard, Nexus Diagnostic Modal, and Reports.

---

## 2. Test Strategy

The platform utilizes a **Layered Testing Approach**:

### 2.1 Unit Testing
- **Focus:** Isolated logic in `ml_service.py` and `utils/__init__.py`.
- **Tool:** Python `unittest` framework.
- **Criteria:** Verify math interaction terms and sensor validation bounds.

### 2.2 Integration Testing
- **Focus:** Data flow between Flask, PostgreSQL, and the ML artifacts.
- **Tool:** `test_integration.py` within the Docker container.
- **Criteria:** Successful inference results using organizational machine counts.

### 2.3 System Testing
- **Focus:** End-to-end user journeys (Registration → Subscription → Fleet Monitoring).
- **Tool:** Manual browser-based audit.
- **Criteria:** Zero "Machine #undefined" errors and correct plan highlighting.

### 2.4 User Acceptance Testing (UAT)
- **Focus:** Operational usability for Maintenance Engineers.
- **Criteria:** Diagnostic reports must be interpretable within < 5 seconds of clicking.

---

## 3. Scope of Testing

### 3.1 Features to be Tested
- [ ] **Multi-Tenancy:** Verify users from domain A cannot see assets from domain B.
- [ ] **STK Push Lifecycle:** Verify initiation, callback, and proactive polling fallback.
- [ ] **Fleet Scaling:** Verify dashboard displays 10, 44, or 100 machines accurately.
- [ ] **Input Sanitization:** Verify rejection of extreme integers (e.g., Temperature > 1000K).
- [ ] **XAI Consistency:** Ensure modal risk % matches dashboard tile gauges.

### 3.2 Features NOT to be Tested
- **Live PLC Integration:** Hardware sensor connectivity is mocked by the AI4I 2020 dataset.
- **Global SMS Delivery:** Relying on PayHero/Safaricom gateway for final message delivery.

---

## 4. Pass/Fail Criteria

| Test Category | Pass Condition | Fail Condition |
|---------------|----------------|----------------|
| **ML Recall** | > 95% on failure detection | Missed catastrophic failure alert |
| **Payment** | Status updated < 10s post-PIN | Manual DB intervention required |
| **Security** | 403 Forbidden on foreign IDs | Unauthorized data access |
| **Stability** | 0 Crashes during fleet re-score | Gunicorn worker timeout |

---

## 5. Test Environment

- **Local:** SQLite in-memory, Docker Compose (Postgres 15), Redis 7.
- **Public:** Ngrok HTTPS tunnel for M-Pesa callback verification.
- **Production:** Render Blueprint environment (Managed DB/Redis).

---

## 6. Suspension & Resumption Requirements

- **Suspension:** Testing shall be suspended if the PayHero API is unreachable or if ML model checksums fail.
- **Resumption:** Testing resumes once connectivity is verified or model artifacts are re-synchronized.

---
**Last Updated:** March 2026  
**Status:** **APPROVED FOR EXECUTION**
