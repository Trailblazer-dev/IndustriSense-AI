#!/bin/bash
# IndustriSense AI Web Application Startup Script (macOS/Linux)

echo ""
echo "===================================="
echo "IndustriSense AI - Web Application"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Start the application
echo ""
echo "===================================="
echo "Starting Flask Application"
echo "===================================="
echo ""
echo "Server running at: http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo ""

python app.py
