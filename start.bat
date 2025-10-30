@echo off
echo 🏀 NBA Player Comparison Tool Setup
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

REM Install dependencies
echo Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo Starting Flask server...
echo Open your browser and navigate to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py
