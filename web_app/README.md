# Flask Web Application Setup

## Installation

1. **Navigate to web_app directory:**
```bash
cd web_app
```

2. **Create a virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode
```bash
python app.py
```
The application will be available at: `http://localhost:5000`

### Production Mode
```bash
set FLASK_ENV=production  # Windows
# or
export FLASK_ENV=production  # macOS/Linux

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Project Structure

```
web_app/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   ├── base.html            # Base template with navbar
│   ├── dashboard.html       # Machine status dashboard
│   ├── analytics.html       # Feature importance analysis
│   ├── models.html          # Model details and performance
│   ├── predict.html         # Prediction interface
│   ├── settings.html        # Settings configuration
│   ├── about.html           # About and documentation
│   └── error.html           # Error page
└── static/
    ├── css/
    │   └── style.css        # Main stylesheet
    └── js/
        └── main.js          # JavaScript utilities
```

## Features

### 1. Dashboard
- Real-time machine status overview
- Risk classification (Critical/Warning/Normal)
- Tool wear and RUL estimates
- Interactive machine details modal

### 2. Analytics
- Feature importance visualizations
- Model performance insights
- Classifier vs Regressor comparison
- Key insights and findings

### 3. Models
- Classifier architecture and specs
- Regressor architecture and specs
- System architecture diagram
- Model performance comparison

### 4. Prediction
- Manual machine parameter input
- Real-time prediction generation
- Automatic feature calculation
- Actionable recommendations

### 5. Settings
- Alert threshold configuration
- Notification preferences
- Data retention policies
- Developer settings

### 6. About
- Project overview
- Technology stack details
- System architecture explanation
- Limitations and constraints
- Future roadmap (Phase 2)

## API Endpoints

### Dashboard Data
- `GET /` - Main dashboard page
- `GET /api/stats` - Overall system statistics
- `GET /api/machines/<id>` - Details for specific machine

### Predictions
- `POST /api/predict` - Generate prediction for new data

### Pages
- `GET /analytics` - Feature importance analysis
- `GET /models` - Model details and comparison
- `GET /predict` - Prediction interface
- `GET /settings` - Settings page
- `GET /about` - About page

## Configuration

### Environment Variables
Set in `config.py` or as environment variables:

```python
FLASK_ENV=development  # or production
SECRET_KEY=your-secret-key
```

### Model Paths
By default, the app looks for trained models in:
```
../src/models/
  ├── xgboost_classifier.pkl
  └── xgboost_wear_regressor.pkl
```

### Data Paths
Feature-engineered data expected at:
```
../data/processed/
  └── features_engineered_raw.csv
```

## Usage Examples

### Starting the Server
```bash
# Development
python app.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Making Predictions via API
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [295.3, 310.0, 1500, 42.8, 0, 50, 14.7, 0, 63000000, 0]
  }'
```

### Accessing Dashboard
Open browser and navigate to: `http://localhost:5000`

## Troubleshooting

### Models Not Found
Ensure trained models exist in `../src/models/` directory:
- `xgboost_classifier.pkl`
- `xgboost_wear_regressor.pkl`

### Data Not Loading
Check that data file exists at:
- `../data/processed/features_engineered_raw.csv`

### Port Already in Use
Change port in `app.py`:
```python
app.run(host='127.0.0.1', port=8000)  # Change 5000 to 8000
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps (Phase 2)

Planned enhancements:
- [ ] Real-time data streaming integration
- [ ] Model retraining pipeline
- [ ] Feedback loop for continuous improvement
- [ ] Historical data dashboard
- [ ] Advanced visualization library (Chart.js, Plotly)
- [ ] Mobile responsive improvements
- [ ] Database integration (SQLAlchemy)
- [ ] Authentication/Authorization
- [ ] API rate limiting
- [ ] Docker containerization

## Support

For issues or questions, refer to:
- Main README: `../README.md`
- Project documentation: `../docs/`
- Notebook 5 XAI: `../notebooks/5_XAI_and_Interpretation.ipynb`
