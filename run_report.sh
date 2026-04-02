#!/bin/bash

# Report generation wrapper script for Linux/macOS
# This script handles virtualenv activation and error logging
# 
# Usage:
#   ./run_report.sh
#
# Cron example:
#   0 6 * * * /path/to/daily-report-automation-python/run_report.sh >> /path/to/cron.log 2>&1

set -e

# Project directory (modify this if needed)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Log file
LOG_FILE="$PROJECT_DIR/execution.log"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to handle errors
handle_error() {
    log_message "ERROR: Report generation failed with exit code $?"
    exit 1
}

trap handle_error ERR

# Log start
log_message "=========================================="
log_message "Starting MTD Report Generation"
log_message "=========================================="

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    log_message "ERROR: Virtual environment not found at $PROJECT_DIR/venv"
    log_message "Run: python3 -m venv $PROJECT_DIR/venv"
    exit 1
fi

# Activate virtual environment
log_message "Activating virtual environment..."
source "$PROJECT_DIR/venv/bin/activate"

# Change to project directory
cd "$PROJECT_DIR"

# Set environment variables
export LOG_LEVEL=INFO
export PYTHONUNBUFFERED=1

# Run the report generator
log_message "Running report generator..."
python main.py

# Check result
if [ $? -eq 0 ]; then
    log_message "✓ Report generation completed successfully"
    log_message "=========================================="
    exit 0
else
    log_message "✗ Report generation failed"
    log_message "=========================================="
    exit 1
fi
