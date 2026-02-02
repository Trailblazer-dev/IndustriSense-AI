@echo off
REM Quick start with existing ml_env
REM Run this if you already have ml_env environment

echo Activating ml_env...
call C:\Users\richv\anaconda3\Scripts\activate.bat ml_env

echo Installing Flask dependencies...
pip install flask flask-cors pandas numpy scikit-learn xgboost matplotlib seaborn -q

echo.
echo Starting Flask Application at http://localhost:5000
echo Press CTRL+C to stop
echo.

cd /d D:\vscode\IndustriSense-AI\web_app
python app.py

pause
