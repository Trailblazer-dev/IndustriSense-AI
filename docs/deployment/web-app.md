# 🌐 IndustriSense AI - Web Application Documentation

This document provides a comprehensive guide to the architecture, deployment, and operational logic of the IndustriSense AI SaaS platform.

---

## 🏛️ Application Architecture

IndustriSense AI is built as a modern, secure, and high-performance SaaS platform using the **Flask** ecosystem. It follows a modular design focused on Human-Computer Interaction (HCI) and industrial-grade reliability.

### Core Stack
- **Framework:** Flask 3.0.0 (Python Web Framework)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Flask-Login with secure session management
- **Security:** Flask-WTF (CSRF), Flask-Limiter (Rate Limiting), Flask-Talisman (Secure Headers)
- **ML Engine:** XGBoost 3.2.0 (Vectorized batch inference)
- **UI/UX:** Bootstrap 5 with custom "Modern Industrial" Glassmorphism theme

---

## 📁 Directory Structure

```text
web_app/
├── app.py                  # Main Application logic & Routing
├── models.py               # Database Schema (Users, Transactions)
├── config.py               # Environment-based Configuration
├── requirements.txt        # Dependency Management
│
├── static/                 # Frontend Assets
│   ├── css/style.css       # Premium HCI-optimized styling
│   └── js/main.js          # Interactive UI logic & API helpers
│
├── templates/              # Public & Private Views
│   ├── index.html          # Public Landing Page
│   ├── login.html          # Secure Sign-in
│   ├── register.html       # Account Creation
│   ├── dashboard.html      # Private Fleet Monitor (Auth required)
│   ├── predict.html        # Manual Diagnostics (Auth + Plan required)
│   ├── analytics.html      # Model Insights (Auth + Plan required)
│   └── ...                 # Pricing, About, Error pages
│
└── industrisense.db        # Local persistence layer (SQLite)
```

---

## 🛡️ Security & Access Control

IndustriSense AI prioritizes data integrity and user isolation through multiple security layers.

### 1. Multi-Tenancy
Data is strictly isolated at the query level. The `/dashboard` route uses `get_user_machines()` to ensure users only see assets assigned to their specific account ID.

### 2. Role-Based Access Control (RBAC)
Features are restricted based on the user's subscription tier:
- **Free**: Public spec pages and Basic Fleet Monitor.
- **Starter**: Unlocks **Advanced Analytics**.
- **Professional**: Unlocks **Manual Diagnostics (Predict)** and API access.
- **Enterprise**: Unlocks **System Calibration** and high-frequency monitoring.

**Note on RUL Accuracy**: As of Version 3.0, the data leakage in the RUL regressor has been successfully remediated. The model now uses clean sensor telemetry exclusively, providing realistic maintenance forecasting.

### 3. Defensive Security
- **CSRF Protection**: Every state-changing request (`POST`) is verified via a secure token.
- **Rate Limiting**: Throttles brute-force attempts on Login (20/hr) and Registration (10/hr).
- **Secure Headers**: Enforces Content Security Policy (CSP) and HSTS via Talisman.

---

## 🚀 Deployment & Operation

### Environment Configuration
Configure your `.env` file for production:
```env
FLASK_ENV=production
SECRET_KEY=your-secure-random-key
PAYHERO_API_KEY=pk_live_...
TALISMAN_FORCE_HTTPS=True
```

### Running the Application
**Development:**
```bash
python app.py
```

**Production (Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🔌 API Reference

All API endpoints (except public specs) require an active session and follow plan-based restrictions.

| Endpoint | Method | Plan Required | Description |
|----------|--------|---------------|-------------|
| `/api/stats` | GET | Free | Aggregate health metrics for the user's fleet. |
| `/api/machines/<id>` | GET | Free | Detailed telemetry and AI variance report. |
| `/api/predict` | POST | Professional | Custom inference using raw sensor data. |

---

## 📊 Data & Inference Flow

1. **Request**: User visits `/dashboard`.
2. **Auth**: Flask-Login verifies the session.
3. **Multi-Tenancy**: `get_user_machines` filters the global dataset for the user's ID.
4. **Vectorized Inference**: 
   - **Classifier**: Receives **Scaled Data** for failure probability.
   - **Regressor**: Receives **Raw Data** for tool wear/RUL estimation.
5. **HCI Rendering**: Data is formatted into "Health Tiles" with color-coded risk alerts.

---

**Version:** 3.0 (SaaS Edition)  
**Last Updated:** March 11, 2026  
**Status:** Production Hardened
