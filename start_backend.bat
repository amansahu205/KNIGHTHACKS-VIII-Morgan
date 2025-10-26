@echo off
echo Starting Backend Server...
echo.

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and add your API keys
    exit /b 1
)

REM Load environment variables from .env
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    set "line=%%a"
    if not "!line:~0,1!"=="#" (
        set "%%a=%%b"
    )
)

echo Starting uvicorn server...
echo Backend will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
