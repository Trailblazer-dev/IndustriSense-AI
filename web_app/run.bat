@echo off
REM IndustriSense AI Web Application Startup Script (Windows)

echo.
echo ====================================
echo IndustriSense AI - Web Application
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies with only pre-built wheels
echo Installing dependencies...
echo This may take a minute...
pip install --only-binary :all: flask flask-cors python-dotenv
pip install --only-binary :all: numpy pandas scikit-learn xgboost matplotlib seaborn

REM Start the application
echo.
echo ====================================
echo Starting Flask Application
echo ====================================
echo.
echo Server running at: http://localhost:5000
echo Press CTRL+C to stop the server
echo.

python app.py

pause
