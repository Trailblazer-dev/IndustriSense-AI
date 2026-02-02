"""
IndustriSense AI - Flask Web Application
A comprehensive predictive maintenance system with ML-powered predictions
and professional dashboard interface.

Run this file to start the web application:
    python app.py

Then open your browser to: http://localhost:5000
"""

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                  IndustriSense AI - Web App                   ║
    ║            Predictive Maintenance Dashboard                   ║
    ╚════════════════════════════════════════════════════════════════╝
    
    📍 Starting Flask Application...
    
    """)
    
    from app import app
    
    print(f"""
    ✅ Server Status: Running
    
    🌐 Access the application:
       • Dashboard: http://localhost:5000
       • Analytics: http://localhost:5000/analytics
       • Models:    http://localhost:5000/models
       • Predict:   http://localhost:5000/predict
       • Settings:  http://localhost:5000/settings
       • About:     http://localhost:5000/about
    
    🛑 To stop the server: Press CTRL+C
    
    ─────────────────────────────────────────────────────────────────
    """)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
