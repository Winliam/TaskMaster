@echo off
chcp 65001 >nul
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.7+.
    pause
    exit /b 1
)

set SESSION_SECRET=very-secure-session-key
set DATABASE_URL=sqlite:///education_management.db

echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install flask flask-sqlalchemy flask-login flask-wtf email_validator pypinyin
)

echo Starting server...
start "" python main.py

timeout /t 2 >nul

echo Opening browser...
start "" http://localhost:5000

echo.
echo System started! Use username=admin, password=admin to login.
echo Press any key to stop the server...
pause >nul
taskkill /f /im python.exe >nul 2>&1