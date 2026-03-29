# 📚 IndustriSense AI Documentation

Technical specifications, guides, and operational manuals for the IndustriSense AI platform.

---

## 🚀 Quick Navigation

### 👤 **Getting Started**
- **[User Guide Manual](guides/user-manual.md)** - Comprehensive guide for operators and managers.
- **[Quick Start Guide](guides/quick-start.md)** - 3-step setup and overview.
- **[Retraining Guide](RETRAINING_GUIDE.md)** - How to update models with new data.

### 👨‍💻 **Developer Reference**
- **[Web App Documentation](deployment/web-app.md)** - Flask architecture, security, and deployment.
- **[ML Troubleshooting](deployment/ml-troubleshooting.md)** - Common issues, feature scaling, and debugging.
- **[Verification Checklist](deployment/verification.md)** - Pre-deployment testing procedures.

### 📝 Technical Specifications
- **[SRS (Requirements)](project/SRS.md)** - Functional and non-functional requirements.
- **[SDD (Design)](project/SDD.md)** - System architecture and component design.
- **[Database Schema](project/DATABASE_SCHEMA.md)** - Relational data model and ER diagrams.
- **[Test Plan](project/TEST_PLAN.md)** - Verification strategy and industrial quality standards.
- **[Notebooks Overview](notebooks/README.md)** - Data science pipeline and experimental results.


---

## 📂 Documentation Structure

```
docs/
├── README.md                       ← You are here
├── RETRAINING_GUIDE.md             ← Model update procedures
│
├── guides/                         ← Getting Started
│   └── quick-start.md             Installation & usage
│
├── deployment/                     ← Operations & DevOps
│   ├── web-app.md                 Flask & Gunicorn guide
│   ├── ml-troubleshooting.md       ML pipeline debugging
│   ├── verification.md             Testing checklist
│   └── changes.md                  Technical changelog
│
├── notebooks/                      ← Data Science
│   ├── README.md                  Notebook index & results
│   └── [specific notebooks...]     Technical details
│
└── project/                        ← Product Specs
    ├── SRS.md                      System requirements
    └── SDD.md                      Architecture & design
```

---

## 👔 Subscription Tiers & Access

| Tier | Target Audience | Key Capabilities |
|------|-----------------|------------------|
| **Operational Base** | Entry-level Monitoring | 10 Machines, Failure Classification, Basic XAI. |
| **Production Pro** | Maintenance Teams | 50 Machines, RUL Forecasting, Maintenance Reports. |
| **Industrial Nexus** | Enterprise ROI | Unlimited Machines, Full CMMS Integration, Financial Audits. |

---

## 🔄 Version Information

**Current Version:** 3.5 (Industrial Hardened)  
**Last Updated:** March 2026  
**Status:** Production Ready
