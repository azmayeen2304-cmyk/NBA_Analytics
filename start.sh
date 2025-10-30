#!/bin/bash

echo "🏀 NBA Player Comparison Tool Setup"
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
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting Flask server..."
echo "Open your browser and navigate to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py
