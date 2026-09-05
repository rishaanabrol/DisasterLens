@echo off
setlocal enabledelayedexpansion

:: Change to directory where run.bat is located
cd /d "%~dp0"

echo =====================================================
echo Starting DER-01 AI Backend API
echo =====================================================

:: Ensure Python scripts and executable paths are included in PATH
set "PATH=%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts;%LOCALAPPDATA%\Python\pythoncore-3.14-64;%LOCALAPPDATA%\Python\bin;%APPDATA%\Python\Python314\Scripts;C:\Python314\Scripts;C:\Python314;%PATH%"

:: Locate Python executable
set "PYTHON_CMD="
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
) else if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Python\bin\python.exe"
) else if exist "C:\Python314\python.exe" (
    set "PYTHON_CMD=C:\Python314\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    ) else (
        where py >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON_CMD=py"
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python not found. Please install Python.
    pause
    exit /b 1
)

:: Verify dependencies (uvicorn, fastapi, pillow, multipart)
"%PYTHON_CMD%" -c "import uvicorn, fastapi, PIL" >nul 2>nul
if errorlevel 1 (
    echo [INFO] Installing required dependencies...
    "%PYTHON_CMD%" -m pip install uvicorn fastapi pillow python-multipart
)

echo.
echo =====================================================
echo Server running at: http://127.0.0.1:8000
echo You can now open index.html in your browser!
echo (Keep this window open to run the AI backend)
echo =====================================================
echo.

"%PYTHON_CMD%" -m uvicorn app:app --host 127.0.0.1 --port 8000

if errorlevel 1 (
    echo.
    echo Server stopped unexpectedly.
    pause
)

