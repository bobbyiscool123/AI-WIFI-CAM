@echo off
echo AI WiFi CAM - Startup Script
echo ==========================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python 3.7 or newer.
    goto :error
)

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        goto :error
    )
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    goto :error
)

REM Check if requirements are installed
if not exist venv\Lib\site-packages\opencv (
    echo Installing required packages...
    pip install -r pc_code\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install required packages.
        goto :error
    )
)

REM Check if model files exist
if not exist models\yolov4.weights (
    echo Downloading model files...
    python pc_code\download_models.py
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download model files.
        goto :error
    )
)

REM Run the system check
echo Running system compatibility check...
python pc_code\check_system.py
if %ERRORLEVEL% NEQ 0 (
    echo System check failed. Please check the output above.
    goto :error
)

echo.
echo Starting AI WiFi CAM...
echo Press Ctrl+C to stop the server.
echo.

REM Run the main script
python pc_code\stream_receiver.py %*

goto :end

:error
echo.
echo An error occurred. Please check the output above.
pause
exit /b 1

:end
echo.
echo AI WiFi CAM has stopped.
pause
