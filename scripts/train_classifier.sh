#!/bin/bash
# Script to run Failure Classifier retraining

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "web_app/venv" ]; then
    source web_app/venv/bin/activate
fi

echo "Starting Failure Classifier Retraining..."
python3 -m src.models.train_classifier

if [ $? -eq 0 ]; then
    echo "Retraining process finished successfully."
else
    echo "Retraining process failed."
    exit 1
fi
