# 🌐 Web Application Documentation

Complete guide to the IndustriSense-AI Flask dashboard.

---

## Overview

IndustriSense-AI includes a professional web application built with **Flask** and **XGBoost** that provides:

✅ Real-time machine monitoring dashboard  
✅ Interactive failure risk predictions  
✅ Feature importance analysis  
✅ Tool wear and RUL estimation  
✅ RESTful API for integrations  
✅ Responsive design (desktop, tablet, mobile)  

---

## Quick Start

### Windows
```powershell
cd web_app
.\run.bat
```

### macOS/Linux
```bash
cd web_app
./run.sh
```

### Manual Setup
```bash
cd web_app
pip install -r requirements.txt
python app.py
```

**Access:** `http://localhost:5000`

---

## Application Structure

```
web_app/
├── app.py                      ← Flask application (500+ lines)
├── config.py                   ← Configuration management
├── requirements.txt            ← Dependencies
├── __main__.py                 ← Entry point with ASCII art
│
├── templates/                  ← HTML pages (6 total)
│   ├── base.html              ← Base layout & navigation
│   ├── dashboard.html         ← Machine monitoring (200+ lines)
│   ├── analytics.html         ← Feature analysis (150+ lines)
│   ├── models.html            ← Model details (300+ lines)
│   ├── predict.html           ← Prediction form (250+ lines)
│   ├── settings.html          ← Configuration (300+ lines)
│   ├── about.html             ← Documentation (400+ lines)
│   └── error.html             ← Error handling
│
└── static/
    ├── css/
    │   └── style.css          ← Styling (1000+ lines, responsive)
    └── js/
        └── main.js            ← Utilities & API helpers
```

---

## Web Pages

### 1. Dashboard (`/`)

**Real-time machine monitoring interface**

**Features:**
- **System Statistics** - Total machines, Critical, Warning, Normal counts
- **Machine Status Cards** - 10 sample machines with:
  - Failure risk percentage (color-coded)
  - Actual vs. Predicted tool wear
  - Actual vs. Predicted RUL
  - Error metrics
  - Interactive detail button

**Data Display:**
```
Machine #6252        [WARNING]
Failure Risk: 73.2%  ═══[73.2%]═══
Actual Tool Wear: 198.0 min
Predicted Wear: 195.3 min (Error: ±2.7 min, 1.1%)
Actual RUL: 55 min
Predicted RUL: 58 min
[More Details...]
```

**Features:**
- Color-coded risk levels:
  - 🔴 Red (70-100%): Critical - Take action immediately
  - 🟡 Yellow (30-69%): Warning - Monitor closely
  - 🟢 Green (0-29%): Normal - Operating safely
- Auto-refreshes every 30 seconds
- Click "More Details" for comprehensive machine analysis
- Responsive grid layout

---

### 2. Analytics (`/analytics`)

**Feature importance and model interpretation**

**Shows:**
- **Failure Classifier Importance** (10 features)
  - Ranked by contribution to failure prediction
  - Tool Temperature Difference dominates (highest impact)
  - Visual bar charts for easy comparison

- **Wear Regressor Importance** (9 features)
  - Ranked by contribution to wear estimation
  - Interaction terms (Temp_Diff_x_Wear) most important
  - Feature correlation insights

Example importance rankings:
```
Classifier Top Features:
1. Temp Difference [K]     72.5%  ▓▓▓▓▓▓▓▓▓▓
2. Stress Index            19.8%  ▓▓▓░░░░░░░
3. Tool Wear [min]         5.1%   ▓░░░░░░░░░
...

Regressor Top Features:
1. Temp_Diff_x_Wear       71.2%  ▓▓▓▓▓▓▓▓▓▓
2. Stress Index            21.8%  ▓▓▓░░░░░░░
3. Torque [Nm]             3.7%   ▓░░░░░░░░░
...
```

---

### 3. Models (`/models`)

**Technical specifications and performance metrics**

**Displays:**
- **XGBoost Classifier**
  - Objective: Binary classification (Machine failure yes/no)
  - Input features: 10 (temperature, torque, speed, etc.)
  - Performance: 98.8% accuracy, 0.982 ROC-AUC
  - Training samples: 8,000

- **XGBoost Regressor**
  - Objective: Continuous value regression (Tool wear minutes)
  - Input features: 9 (excludes target to prevent leakage)
  - Performance: R²=0.9996, MAE=0.88 min, RMSE=1.37 min
  - Training samples: 8,000

**System Architecture:**
```
Raw Features (10 inputs)
         ↓
[Feature Engineering]
  - Create Stress Index
  - Calculate Temp Differential
  - Isolation Forest anomaly detection
         ↓
Feature Matrix (16 engineered features)
         ↓
    ┌────┴────┐
    ↓         ↓
[Classifier]  [Regressor]
    ↓         ↓
Failure Risk  Tool Wear/RUL
    ↓         ↓
  0-100%     0-253 min
```

---

### 4. Predict (`/predict`)

**Interactive prediction interface for custom scenarios**

**Inputs (10 fields):**
1. Air Temperature [K] - Range: 295-305 K
2. Process Temperature [K] - Range: 300-320 K
3. Rotational Speed [rpm] - Range: 1000-3000 rpm
4. Torque [Nm] - Range: 3-80 Nm
5. Tool Wear Target - Optional (if known)
6. Humidity - Optional
7. Power - Optional
8. Stage - Optional (0-51 stage number)
9. Product Type - Select from dropdown
10. Process Type - Select tool type

**Outputs:**
- Failure Probability (0-100%)
- Failure Risk Level (Normal/Warning/Critical)
- Predicted Tool Wear (min)
- Predicted RUL (remaining useful life in min)
- Feature interaction preview

**Recommendation Engine:**
```
If Failure Prob < 30%:
  ✓ Status: NORMAL - Continue operation
  
If Failure Prob 30-70%:
  ⚠ Status: WARNING
  → Increase inspection frequency
  → Check bearing condition
  → Plan maintenance window
  
If Failure Prob > 70%:
  ✗ Status: CRITICAL
  → Stop operation immediately
  → Inspect all components
  → Schedule emergency maintenance
```

---

### 5. Settings (`/settings`)

**System configuration and preferences**

**Configurable Options:**
- Alert threshold adjustment (default: 70% failure probability)
- Notification preferences
- Auto-refresh interval (default: 30 sec)
- Data display format preferences
- Developer mode toggle

**Save/Reset buttons** for configuration persistence

---

### 6. About (`/about`)

**Project overview and documentation**

**Sections:**
- System description and capabilities
- Feature showcase (6 feature cards)
- Technology stack (Python, XGBoost, Flask, SHAP)
- System architecture explanation
- 5-step process workflow diagram
- System limitations (important!)
- Team information
- Version and roadmap

---

## API Endpoints

### Get System Statistics
```
GET /api/stats

Response:
{
  "total_machines": 10,
  "critical_count": 2,
  "warning_count": 4,
  "normal_count": 4,
  "timestamp": "2024-02-22 14:30:00"
}
```

### Get Machine Details
```
GET /api/machines/<machine_id>

Example: GET /api/machines/5

Response:
{
  "id": 5,
  "failure_probability": 0.532,
  "actual_tool_wear": 145.2,
  "predicted_tool_wear": 142.8,
  "wear_error": 2.4,
  "actual_rul": 107,
  "predicted_rul": 110,
  "status": "WARNING"
}
```

### Make Predictions
```
POST /api/predict

Request Body:
{
  "air_temp": 300.5,
  "process_temp": 310.2,
  "rpm": 1500,
  "torque": 42.5,
  "humidity": 0.5,
  "power": 5.2
}

Response:
{
  "failure_probability": 0.456,
  "failure_status": "WARNING",
  "predicted_wear": 87.3,
  "predicted_rul": 165.7,
  "features_used": 10
}
```

---

## Design Features

### Responsive Layout
- **Desktop (1200px+):** Multi-column grids, side-by-side comparisons
- **Tablet (768-1200px):** 2-column layout with optimized spacing
- **Mobile (<768px):** Single column, stacked cards, full-width forms

### Color Scheme
- **Primary:** Purple → Cyan gradient (professional, modern)
- **Accent:** Pink for highlights
- **Status Colors:**
  - 🔴 Red (#f5576c): Critical
  - 🟡 Yellow (#ffc107): Warning
  - 🟢 Green (#4CAF50): Normal
  - 🔵 Blue (#2196F3): Actual/Ground truth values
  - 🟠 Orange (#FF9800): Predicted values

### Accessibility
- Semantic HTML structure
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast color ratios
- Form validation and error messages

---

## Configuration

### Environment Variables (`web_app/config.py`)

```python
# Data directory
DATA_DIR = '../data/processed/'

# Model directory
MODEL_DIR = '../src/models/'

# Flask settings
DEBUG = False                  # Set True for development
HOST = '127.0.0.1'           # Localhost only
PORT = 5000                   # Default port
THREADED = True              # Enable threading for concurrent requests
```

### Running in Different Modes

**Development (with hot reload):**
```bash
FLASK_ENV=development python app.py
```

**Production (with gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Data Flow

```
1. User Request (e.g., Dashboard load)
           ↓
2. Flask Route Handler (@app.route('/'))
           ↓
3. Load Data: load_data() → features_engineered_raw.csv
           ↓
4. Load Models: pickle.load(classifier, regressor)
           ↓
5. Prepare Features: 
   - Extract 10 features for classifier
   - Extract 9 features for regressor
           ↓
6. Make Predictions:
   - classifier.predict_proba() → failure probability
   - regressor.predict() → tool wear estimate
           ↓
7. Calculate Secondary Values:
   - RUL = 253 - predicted_wear
   - Status = categorize by probability
           ↓
8. Format for Display (JSON or HTML)
           ↓
9. Return Response to User
```

---

## Performance Optimization

- **Models loaded once at startup** (not reloaded per request)
- **Data cached in memory** for 1000 samples (configurable)
- **JSON API responses** minimize data transfer
- **CSS/JS minification** for faster loading
- **Efficient CSS Grid** layout (no Bootstrap bloat)

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

### Models Not Loading
- Verify files exist: `src/models/xgboost_*.pkl`
- Check permissions: Ensure read access
- Check paths: Verify `MODEL_DIR` in config.py

### Predictions Incorrect
- See [ml-troubleshooting.md](ml-troubleshooting.md) for debugging
- Check feature scaling matches training
- Verify data files are loaded correctly

### CSS/JS Not Loading
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)
- Check `STATIC_FOLDER` path in config.py

---

## Related Documentation

- [ML Troubleshooting Guide](ml-troubleshooting.md) - Common issues and fixes
- [Verification Checklist](verification.md) - Testing procedures
- [ML Pipeline Documentation](../architecture/ml-pipeline.md) - Model details
- [Quick Start Guide](../guides/quick-start.md) - Getting started

---

**Version:** 2.0  
**Last Updated:** February 22, 2026  
**Status:** Production Ready
