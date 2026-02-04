# 🏭 IndustriSense AI - Full Website Complete!

Your Flask web application is now ready to deploy! Here's everything you have:

## 📦 What You Got

### Core Flask Application (`web_app/`)
- **app.py** - Main Flask application with routes and API endpoints
- **config.py** - Configuration management for dev/prod environments
- **requirements.txt** - All Python dependencies
- **Startup scripts** - `run.bat` (Windows) and `run.sh` (macOS/Linux)

### 6 Professional Web Pages
1. **Dashboard** (`/`) - Machine status overview with real-time stats
2. **Analytics** (`/analytics`) - Feature importance analysis and insights
3. **Models** (`/models`) - Model architecture and performance details
4. **Predict** (`/predict`) - Interactive prediction interface
5. **Settings** (`/settings`) - Configuration and preferences
6. **About** (`/about`) - Project overview and documentation

### API Endpoints (RESTful)
- `GET /api/stats` - System statistics
- `GET /api/machines/<id>` - Machine details
- `POST /api/predict` - Make predictions

### Professional Styling
- Responsive CSS Grid layout (works on desktop, tablet, mobile)
- Modern gradient color schemes
- Interactive components (modals, forms, progress bars)
- Accessible navigation and error handling

---

## 🚀 Quick Start

### Windows Users
```powershell
cd web_app
.\run.bat
```

### macOS/Linux Users
```bash
cd web_app
chmod +x run.sh
./run.sh
```

### Manual Setup
```bash
cd web_app
python -m venv venv
.\venv\Scripts\activate  # or: source venv/bin/activate

pip install -r requirements.txt
python app.py
```

**Then open:** `http://localhost:5000`

---

## 📊 Page Breakdown

### 1. Dashboard (`/`)
**Purpose:** Real-time machine monitoring
- **Features:**
  - Live stats (Total, Critical, Warning, Normal machines)
  - Machine status cards with failure risk percentage
  - Tool wear and RUL display
  - Color-coded risk badges
  - Click for detailed machine analysis
  - Auto-refresh every 30 seconds

### 2. Analytics (`/analytics`)
**Purpose:** Understand model decisions
- **Features:**
  - Feature importance rankings (visual bars)
  - Classifier importance (10 features)
  - Regressor importance (9 features)
  - Key insights on feature relationships
  - ML model interpretation

### 3. Models (`/models`)
**Purpose:** Technical model information
- **Features:**
  - Classifier specifications (XGBoost, 10 features)
  - Regressor specifications (XGBoost, 9 features)
  - Performance metrics comparison
  - System architecture diagram
  - Model comparison table

### 4. Predict (`/predict`)
**Purpose:** Make custom predictions
- **Features:**
  - Input form for all 10 features
  - Auto-calculated interaction features
  - Real-time prediction results
  - Risk classification output
  - RUL estimation
  - Contextual recommendations (Action items based on risk)

### 5. Settings (`/settings`)
**Purpose:** User preferences
- **Features:**
  - System configuration display
  - Alert threshold sliders
  - Auto-refresh interval selection
  - Notification preferences
  - Data retention policy
  - Developer settings

### 6. About (`/about`)
**Purpose:** Project documentation
- **Features:**
  - Project overview
  - Key features showcase
  - Technology stack details
  - System architecture explanation
  - Process flow (5 steps)
  - Limitations (important caveats)
  - Future roadmap (Phase 2 plans)
  - Version information

---

## 🔧 API Usage Examples

### Get System Statistics
```bash
curl http://localhost:5000/api/stats
```

Response:
```json
{
  "total_machines": 10000,
  "critical_count": 120,
  "warning_count": 250,
  "normal_count": 9630,
  "average_failure_risk": 3.39,
  "max_failure_risk": 100.0
}
```

### Make a Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [295.3, 310.0, 1500, 42.8, 50, 50, 14.7, 735, 63000000, 0]
  }'
```

Response:
```json
{
  "success": true,
  "failure_probability": 45.2,
  "tool_wear_minutes": 127.5,
  "remaining_useful_life": 125,
  "risk_level": "WARNING"
}
```

### Get Machine Details
```bash
curl http://localhost:5000/api/machines/42
```

Response:
```json
{
  "machine_id": 42,
  "features": {...},
  "failure_probability": 62.5,
  "tool_wear_minutes": 98.2,
  "remaining_useful_life": 154
}
```

---

## 📁 File Structure

```
web_app/
├── app.py                         # Main Flask application
├── config.py                      # Configuration settings
├── __main__.py                    # Entry point
├── requirements.txt               # Python dependencies
├── README.md                      # Web app documentation
├── run.bat                        # Windows startup script
├── run.sh                         # Unix startup script
│
├── templates/                     # HTML templates
│   ├── base.html                 # Base layout (navbar, footer)
│   ├── dashboard.html            # Machine overview page
│   ├── analytics.html            # Feature analysis page
│   ├── models.html               # Model details page
│   ├── predict.html              # Prediction interface page
│   ├── settings.html             # Settings configuration page
│   ├── about.html                # Project information page
│   └── error.html                # Error page
│
└── static/                        # Static files
    ├── css/
    │   └── style.css             # Main stylesheet (1000+ lines)
    └── js/
        └── main.js               # JavaScript utilities
```

---

## 🎨 Design Features

### Responsive Layout
- Desktop (1200px+): 2-3 column grids
- Tablet (768px-1200px): 2 column grids
- Mobile (<768px): 1 column (stacked)

### Color Scheme
- **Primary:** Purple gradient (#667eea → #764ba2)
- **Critical:** Red (#f5576c)
- **Warning:** Amber (#ffc107)
- **Normal:** Green (#4CAF50)
- **Secondary:** Cyan gradient (#4facfe → #00f2fe)

### Animations
- Hover effects on cards
- Smooth transitions
- Modal fade-in/slide-in
- Progress bar animations

---

## 🔐 Security Notes

### Development Mode
- Debug mode enabled (default)
- Change `SECRET_KEY` in `config.py` for production
- Set `FLASK_ENV=production` for deployment

### Production Deployment
```python
# config.py - Production setup
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Set via environment
```

```bash
# Deploy with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📝 Data Flow

```
User Input
    ↓
Web Form/API Request
    ↓
Flask Route Handler
    ↓
Load Models & Data
    ↓
Feature Preparation
    ↓
XGBoost Prediction
    ↓
Format Results
    ↓
JSON Response / HTML Render
    ↓
Browser Display
```

---

## 🚨 Important Limitations

From the trained models:

1. **Class Imbalance**: Model is extremely imbalanced (96.6% normal, 3.4% failure)
   - Predictions should be treated as relative risk rankings
   - Not absolute failure probabilities

2. **Snapshot-Based**: Uses instantaneous values, not temporal degradation
   - Cannot predict failures from gradual wear patterns
   - Requires current machine state data

3. **Static Models**: No active learning or retraining
   - Performance may degrade over time
   - Needs manual retraining with new data

4. **Feature Dependent**: Requires all 10 input features
   - Missing features will cause prediction failure
   - Assumes data quality and validity

---

## 🔄 Phase 2 Enhancements (Planned)

- [ ] Real-time data streaming integration
- [ ] Automatic model retraining pipeline
- [ ] User feedback loop for model improvement
- [ ] Prediction history database
- [ ] Advanced charts (Chart.js, Plotly)
- [ ] User authentication/authorization
- [ ] Email/SMS notifications
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Mobile native app

---

## 🆘 Troubleshooting

### Problem: "Models not found"
**Solution:** Ensure pickle files exist in `../src/models/`:
```bash
ls ../src/models/xgboost_*.pkl
```

### Problem: "Data not loaded"
**Solution:** Check CSV exists at `../data/processed/features_engineered_raw.csv`
```bash
ls ../data/processed/
```

### Problem: Port 5000 already in use
**Solution:** Modify port in `app.py`:
```python
app.run(port=8000)  # Use different port
```

### Problem: Import errors
**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Additional Resources

- Main README: [README.md](../README.md)
- Project Docs: [docs/](../docs/)
- ML Notebooks: [notebooks/](../notebooks/)
- Data Files: [data/](../data/)
- Trained Models: [src/models/](../src/models/)

---

## ✅ Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify models exist: `../src/models/xgboost_*.pkl`
- [ ] Verify data exists: `../data/processed/features_engineered_raw.csv`
- [ ] Update `SECRET_KEY` in production
- [ ] Set `FLASK_ENV=production`
- [ ] Use gunicorn or similar WSGI server
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Test all API endpoints

---

## 🎉 You're All Set!

Your professional predictive maintenance website is complete!

**Next steps:**
1. Run the application: `python app.py`
2. Open browser: `http://localhost:5000`
3. Explore all pages and features
4. Test predictions with different machine parameters
5. Review analytics and model insights

Happy deploying! 🚀
