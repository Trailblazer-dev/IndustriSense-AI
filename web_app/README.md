# IndustriSense AI - Web Application

Professional predictive maintenance dashboard for monitoring industrial equipment health, predicting failures, and optimizing maintenance schedules using machine learning.

## ✨ Features

### 🎨 Professional Website
- **Modern Design** using Bootstrap 5
- **Responsive Layout** - Works on all devices
- **Professional Styling** with custom CSS
- **Interactive Components** - Cards, Alerts, Modals
- **Dark/Light Theme Ready** - Future enhancement

### 💳 Payment Integration
- **PayHero Integration** - Secure payment processing
- **Flexible Payment Methods** - M-Pesa, Cards, Bank Transfers
- **3 Pricing Tiers** - Starter, Professional, Enterprise
- **Secure Checkout** - Form validation & encryption
- **Payment Status Tracking** - Success/Failure callbacks

### 📊 Predictive Analytics
- **Machine Failure Detection** - XGBoost Classifier
- **Remaining Useful Life Prediction** - Regression Model
- **Real-time Monitoring** - Live dashboard updates
- **Historical Tracking** - Performance trends
- **Risk Assessment** - Automated failure risk scoring

## 🏗️ Architecture Overview

### Application Stack
- **Framework**: Flask 3.0.0 (Python Web Framework)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- **Payment**: PayHero API Integration
- **ML Models**: XGBoost (Classification & Regression)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Visualization**: Matplotlib, Seaborn
- **Environment**: Python 3.14.2

## 🚀 Quick Start

### Prerequisites
- Python 3.14.2+ installed and in PATH
- Windows, macOS, or Linux
- ~500MB disk space for dependencies

### 1. Navigate to Web App Directory
```powershell
cd web_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
PAYHERO_API_KEY=your_api_key
PAYHERO_API_SECRET=your_api_secret
PAYHERO_SANDBOX=true
```

See [PAYHERO_SETUP_GUIDE.md](PAYHERO_SETUP_GUIDE.md) for detailed PayHero configuration.

### 4. Run Application

**Windows:**
```powershell
.\run.bat
```

**macOS/Linux:**
```bash
bash run.sh
```

**Manual:**
```bash
python app.py
```

Application runs at: `http://localhost:5000`# Run Flask app
python app.py
```

### 4. Access Application
Open browser to: **http://localhost:5000**

## 📊 Pages & Features

### Dashboard (`/`)
Real-time machine monitoring with live statistics
- **Stat Cards**: Total machines, Critical count, Warnings, Normal operations
- **Machine Cards**: 10 sampled machines with failure risk, tool wear, RUL, and status
- **Status Thresholds:**
  - 🔴 **CRITICAL**: Failure risk ≥ 80%
  - 🟡 **WARNING**: Failure risk 50-79%
  - 🟢 **NORMAL**: Failure risk < 50%

### Analytics (`/analytics`)
ML model analysis and feature importance
- Feature importance tables (Classifier & Regressor)
- Visual charts and key insights
- Data-driven recommendations

### Models (`/models`)
Machine learning model specifications
- Classifier: XGBoost Binary Classification (10 features)
- Regressor: XGBoost Regression for Tool Wear (9 features)
- Performance metrics and system architecture

### Predict (`/predict`)
Interactive prediction interface
- 10 input fields for machine parameters
- Real-time failure probability & RUL prediction
- Auto-calculated interaction features

### Settings (`/settings`)
User configuration and preferences
- Alert threshold adjustment
- Notification preferences
- Data retention policies

### About (`/about`)
Project documentation
- Feature showcase
- Technology stack
- System architecture
- Limitations and roadmap

## 🔌 API Endpoints

### GET /api/stats
```json
{
  "total": 10,
  "critical": 2,
  "warning": 3,
  "normal": 5
}
```

### GET /api/machines/<id>
```json
{
  "id": 42,
  "failure_risk": 75.3,
  "tool_wear": 185.2,
  "rul": 68,
  "status": "WARNING"
}
```

### POST /api/predict
```json
{
  "features": [305.2, 310.5, 2000, 45.0, ...]
}
```

## 🗂️ Data & Models

### Input Data
- **Location**: `../data/processed/features_engineered_raw.csv`
- **Records**: 10,000 samples
- **Features**: 10 engineered features for classification, 9 for regression
- **Source**: AI4I 2020 Predictive Maintenance dataset

### Trained ML Models
- **Classifier**: `../src/models/xgboost_classifier.pkl` (binary failure classification)
- **Regressor**: `../src/models/xgboost_wear_regressor.pkl` (tool wear prediction)
- **Importance**: `../src/models/feature_importance.csv`, `wear_feature_importance.csv`

## ⚙️ Configuration

### Environment Variables
**Development** (default):
```powershell
set FLASK_ENV=development
python app.py
```

**Production**:
```powershell
set FLASK_ENV=production
set SECRET_KEY=your-secret-key-here
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📦 Dependencies

```
Flask==3.0.0              # Web framework
Flask-CORS==4.0.0         # Cross-origin requests
pandas>=2.2.0             # Data manipulation (Python 3.14 compatible)
numpy>=2.0.0              # Numerical computing (Python 3.14 compatible)
scikit-learn>=1.3.0       # ML utilities
xgboost>=2.0.0            # Gradient boosting models
matplotlib>=3.8.0         # Data visualization
seaborn>=0.13.0           # Statistical visualization
```

## 🎨 Design

- **Responsive**: Mobile-first design (desktop, tablet, mobile)
- **Color Scheme**: Purple gradient with status colors
- **Components**: Cards, modals, forms, tables, progress bars
- **Animations**: Smooth transitions and hover effects

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
Activate virtual environment first:
```powershell
.\venv\Scripts\activate
python app.py
```

### Port 5000 Already in Use
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Models/Data Files Not Found
Ensure these paths exist:
- `../src/models/xgboost_classifier.pkl`
- `../src/models/xgboost_wear_regressor.pkl`
- `../data/processed/features_engineered_raw.csv`

Run training notebooks if missing:
- Notebook 3: `3_Failure_Classification_Modeling.ipynb`
- Notebook 4: `4_RUL_Prognosis_Modeling.ipynb`

## 🚀 Production Deployment

### Using Gunicorn
```powershell
pip install gunicorn
set FLASK_ENV=production
set SECRET_KEY=your-secret-key
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_ENV=production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📚 Related Notebooks

- **Notebook 1**: `1_EDA.ipynb` - Exploratory data analysis
- **Notebook 2**: `2_Feature_Engineering.ipynb` - Feature creation
- **Notebook 3**: `3_Failure_Classification_Modeling.ipynb` - Classifier
- **Notebook 4**: `4_RUL_Prognosis_Modeling.ipynb` - RUL regressor
- **Notebook 5**: `5_XAI_and_Interpretation.ipynb` - Model interpretation

## 💡 Key Features

✅ Real-time machine monitoring
✅ ML-powered failure prediction
✅ Remaining useful life (RUL) estimation
✅ Feature importance analysis
✅ Interactive prediction interface
✅ Responsive mobile-friendly design
✅ RESTful API endpoints
✅ Professional documentation

---

**Questions?** Check the main project README: `../README.md`
