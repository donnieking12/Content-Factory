@echo off
echo ========================================
echo Content Factory AI - Project Setup
echo ========================================

echo.
echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from:
    echo - Microsoft Store: Search for "Python 3.11"
    echo - OR python.org: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo.
echo Step 2: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Step 3: Activating virtual environment...
call venv\Scripts\activate

echo.
echo Step 4: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 5: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 6: Setting up database...
python setup_db.py
if %errorlevel% neq 0 (
    echo WARNING: Database setup failed - you may need to configure Supabase credentials first
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your API credentials
echo 2. Run: venv\Scripts\activate
echo 3. Run: python run.py
echo.
pause