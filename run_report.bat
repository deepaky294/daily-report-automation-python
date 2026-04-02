@echo off
REM Report generation wrapper script for Windows Task Scheduler
REM 
REM This script handles Python environment activation and error logging
REM 
REM Usage:
REM   run_report.bat
REM
REM For Task Scheduler:
REM   1. Open Task Scheduler
REM   2. Create Basic Task
REM   3. Set Trigger (time and frequency)
REM   4. Action: Start a program
REM   5. Program: C:\path\to\run_report.bat

setlocal enabledelayedexpansion

REM Project directory - modify if needed
set PROJECT_DIR=%~dp0

REM Log file
set LOG_FILE=%PROJECT_DIR%execution.log

REM Log entry point
(
    echo [%date% %time%] ===========================================
    echo [%date% %time%] Starting MTD Report Generation
    echo [%date% %time%] ===========================================
) >> "%LOG_FILE%"

REM Check if virtual environment exists
if not exist "%PROJECT_DIR%venv\Scripts\activate.bat" (
    echo [%date% %time%] ERROR: Virtual environment not found >> "%LOG_FILE%"
    echo ERROR: Virtual environment not found at %PROJECT_DIR%venv
    echo Please run: python -m venv %PROJECT_DIR%venv
    exit /b 1
)

REM Activate virtual environment
"%PROJECT_DIR%venv\Scripts\activate.bat"

if errorlevel 1 (
    echo [%date% %time%] ERROR: Failed to activate virtual environment >> "%LOG_FILE%"
    exit /b 1
)

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Set environment variables
set LOG_LEVEL=INFO

REM Run the report generator
echo [%date% %time%] Running report generator...>> "%LOG_FILE%"
python main.py

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

REM Log result
if %EXIT_CODE% equ 0 (
    (
        echo [%date% %time%] Report generation completed successfully
        echo [%date% %time%] ===========================================
    ) >> "%LOG_FILE%"
    echo Success: Report generated
) else (
    (
        echo [%date% %time%] Report generation failed with exit code %EXIT_CODE%
        echo [%date% %time%] ===========================================
    ) >> "%LOG_FILE%"
    echo Error: Report generation failed with exit code %EXIT_CODE%
)

REM Exit with the same code
exit /b %EXIT_CODE%
