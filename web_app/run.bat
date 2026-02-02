@echo off
REM IndustriSense AI Web Application Startup Script (Windows with Anaconda)

echo.
echo ====================================
echo IndustriSense AI - Web Application
echo ====================================
echo.

REM Initialize Anaconda (required for conda command)
call C:\Users\richv\anaconda3\Scripts\activate.bat

REM Check if ml_env exists, if not create it
echo Checking for ml_env Anaconda environment...
conda env list | findstr "ml_env" >nul
if errorlevel 1 (
    echo Creating ml_env environment...
    conda create -n ml_env python=3.10 -y
)

REM Activate the ml_env environment
echo Activating ml_env environment...
call conda activate ml_env

REM Install dependencies
echo Installing Flask dependencies...
pip install -r requirements.txt -q

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
