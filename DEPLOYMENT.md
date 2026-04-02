# Deployment & Scheduling Guide

This guide covers deploying and scheduling the MTD Report Automation script in various environments.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Linux/macOS Cron Setup](#linuxmacos-cron-setup)
3. [Windows Task Scheduler Setup](#windows-task-scheduler-setup)
4. [Docker Containerization](#docker-containerization)
5. [Production Best Practices](#production-best-practices)
6. [Monitoring & Alerting](#monitoring--alerting)

---

## Development Setup

### Local Testing

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Run the script
python main.py

# Check logs
tail -f logs/mtd_report_automation.log  # On macOS/Linux
type logs\mtd_report_automation.log  # On Windows
```

### Docker Local Testing

```bash
# Build local image
docker build -t mtd-report:latest .

# Run once
docker run --rm mtd-report:latest

# Run with mounted volumes
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  mtd-report:latest
```

---

## Linux/macOS Cron Setup

### Step 1: Prepare the Environment

```bash
# Create a dedicated user (optional but recommended)
sudo useradd -m mtd-report

# Switch to the user
sudo su - mtd-report

# Clone the repository
git clone https://github.com/yourusername/daily-report-automation-python.git
cd daily-report-automation-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Prepare data directory
mkdir -p data
# Copy your Master Report.xlsx, retailer_rm_mapping.csv, etc. to data/

# Return to regular user
exit
```

### Step 2: Create a Script Wrapper

Create `/home/mtd-report/daily-report-automation-python/run_report.sh`:

```bash
#!/bin/bash

# Report generation wrapper script
# This script handles virtualenv activation and error logging

set -e

# Project directory
PROJECT_DIR="/home/mtd-report/daily-report-automation-python"

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Change to project directory
cd "$PROJECT_DIR"

# Set environment variables
export LOG_LEVEL=INFO
export PYTHONUNBUFFERED=1

# Run the report generator
python main.py

# Exit codes:
# 0 = Success
# 1 = Failure
exit $?
```

Make it executable:
```bash
chmod +x /home/mtd-report/daily-report-automation-python/run_report.sh
```

### Step 3: Set Up Cron Job

Edit crontab:
```bash
crontab -e
```

Add one or more of the following:

**Daily at 6:00 AM:**
```cron
0 6 * * * /home/mtd-report/daily-report-automation-python/run_report.sh >> /home/mtd-report/daily-report-automation-python/cron.log 2>&1
```

**Every business day (Mon-Fri) at 5:00 PM:**
```cron
0 17 * * 1-5 /home/mtd-report/daily-report-automation-python/run_report.sh >> /home/mtd-report/daily-report-automation-python/cron.log 2>&1
```

**Multiple times daily (6 AM, 12 PM, 6 PM):**
```cron
0 6,12,18 * * * /home/mtd-report/daily-report-automation-python/run_report.sh >> /home/mtd-report/daily-report-automation-python/cron.log 2>&1
```

**Custom timing help:**
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * * <command>
```

### Step 4: Verify Cron Job

```bash
# List your cron jobs
crontab -l

# Monitor cron logs (varies by system)
sudo tail -f /var/log/cron
# or
sudo journalctl -f -S now
```

### Step 5: Test the Cron Job

```bash
# Run manually to test
/home/mtd-report/daily-report-automation-python/run_report.sh

# Check if output file was created
ls -la /home/mtd-report/daily-report-automation-python/output/

# Check logs
tail -50 /home/mtd-report/daily-report-automation-python/logs/mtd_report_automation.log
```

---

## Windows Task Scheduler Setup

### Step 1: Prepare the Environment

1. **Create a project folder:**
   ```cmd
   mkdir C:\Applications\MTDReportAutomation
   cd C:\Applications\MTDReportAutomation
   ```

2. **Clone and setup:**
   ```cmd
   git clone https://github.com/yourusername/daily-report-automation-python.git .

   python -m venv venv
   venv\Scripts\activate

   pip install -r requirements.txt
   ```

3. **Prepare data:**
   ```cmd
   mkdir data
   mkdir output
   mkdir logs
   # Copy your input files to the data folder
   ```

### Step 2: Create a Batch Script Wrapper

Create `C:\Applications\MTDReportAutomation\run_report.bat`:

```batch
@echo off
REM Report generation wrapper script for Windows Task Scheduler

setlocal enabledelayedexpansion

REM Project directory
set PROJECT_DIR=C:\Applications\MTDReportAutomation

REM Activate virtual environment
call "%PROJECT_DIR%\venv\Scripts\activate.bat"

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Set environment variables
set LOG_LEVEL=INFO

REM Run the report generator
python main.py

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

REM Log the execution
echo %date% %time% - Report generation exited with code %EXIT_CODE% >> "%PROJECT_DIR%\execution.log"

REM Exit with the same code
exit /b %EXIT_CODE%
```

### Step 3: Configure Task Scheduler

1. **Open Task Scheduler:**
   - Press `Win + R`, type `taskschd.msc`, press Enter
   - Or: Control Panel → Administrative Tools → Task Scheduler

2. **Create a New Task:**
   - Right-click on "Task Scheduler Library" → "Create Basic Task"
   - Name: "MTD Report Generation"
   - Description: "Automated daily MTD report generation"

3. **Set Trigger (When to Run):**
   - Click "Triggers" tab → "New"
   - Choose:
     - **Daily** at specific time (e.g., 6:00 AM)
     - Or **On a schedule** → "Daily" → Set time
     - Repeat: Check "Repeat task every" and set interval if needed

4. **Set Action (What to Run):**
   - Click "Actions" tab → "New"
   - Action: "Start a program"
   - Program/script: `C:\Applications\MTDReportAutomation\run_report.bat`
   - Add arguments: (leave empty)
   - Start in: `C:\Applications\MTDReportAutomation`

5. **Set Conditions:**
   - Uncheck "Wake the computer to run this task" (optional)
   - Check "Run task as soon as possible after a scheduled start is missed"

6. **Set Settings:**
   - Check "Stop the task if it runs longer than" → set to 1 hour
   - Check "If the task fails, restart after:" → set to 5 minutes

7. **Click OK** and enter credentials if prompted

### Step 4: Test the Task

```cmd
REM Run the task manually
C:\Applications\MTDReportAutomation\run_report.bat

REM Check if report was generated
dir C:\Applications\MTDReportAutomation\output\

REM Check logs
type C:\Applications\MTDReportAutomation\logs\mtd_report_automation.log
type C:\Applications\MTDReportAutomation\execution.log
```

### Step 5: Monitor Task Execution

1. **Open Task Scheduler**
2. **Navigate to:** Task Scheduler Library
3. **Find:** "MTD Report Generation"
4. **Check:** "Last Run Time", "Last Run Result", "Status"
5. Right-click → "View History" to see all executions

---

## Docker Containerization

### Step 1: Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY src/ ./src/
COPY main.py .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create required directories
RUN mkdir -p data output logs

# Volume mounts for data persistence
VOLUME ["/app/data", "/app/output", "/app/logs"]

# Run the application
CMD ["python", "main.py"]
```

### Step 2: Create Docker Compose File

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mtd-report:
    build: .
    image: mtd-report:latest
    container_name: mtd-report-automation
    
    # Mount volumes
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    
    # Environment variables
    environment:
      LOG_LEVEL: INFO
      MASTER_REPORT_FILE: Master Report.xlsx
      RETAILER_MAPPING_FILE: retailer_rm_mapping.csv
      BEAT_PLAN_FILE: new_beat_plan.csv
    
    # Restart policy
    restart: no
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Step 3: Build and Run

```bash
# Build the image
docker build -t mtd-report:latest .

# Run once
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  mtd-report:latest

# Or use Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

### Step 4: Schedule Docker Container

**Using cron (Linux/macOS):**
```bash
0 6 * * * docker run --rm -v /path/to/data:/app/data -v /path/to/output:/app/output -v /path/to/logs:/app/logs mtd-report:latest
```

**Using Docker Swarm / Kubernetes:**
```bash
# For production, use orchestration platforms
kubectl apply -f deployment.yaml  # Kubernetes example
```

---

## Production Best Practices

### 1. Security

```bash
# Run as non-root user
RUN useradd -m -s /sbin/nologin appuser
USER appuser

# Restrict file permissions
chmod 600 /path/to/config/files
chmod 700 /path/to/scripts
```

### 2. Error Handling

```python
# In your scheduling scripts, always capture exit codes
if [ $? -ne 0 ]; then
    # Send alert
    echo "Report generation failed" | mail -s "MTD Report Error" admin@example.com
fi
```

### 3. Logging

- Store logs in a centralized location
- Use log rotation (already configured in logger.py)
- Archive old logs: `logs/mtd_report_automation.log.{1,2,3,...}`

### 4. Data Backup

```bash
# Backup input data regularly
0 0 * * * tar -czf /backups/mtd-data-$(date +\%Y\%m\%d).tar.gz /path/to/data/

# Keep last 30 days
find /backups -name "mtd-data-*.tar.gz" -mtime +30 -delete
```

### 5. Monitoring

Create a monitoring script `monitor_report.sh`:

```bash
#!/bin/bash

# Check if report was generated today
TODAY=$(date +%d-%m-%Y)
REPORT_FILE="output/MTD report $TODAY.xlsx"

if [ -f "$REPORT_FILE" ]; then
    echo "✓ Report generated successfully"
    exit 0
else
    echo "✗ Report NOT found: $REPORT_FILE"
    # Send alert
    mail -s "MTD Report Generation Failed" admin@example.com < /dev/null
    exit 1
fi
```

---

## Monitoring & Alerting

### Prometheus Metrics (Optional)

Add to `main.py`:

```python
from prometheus_client import Counter, Gauge, start_http_server
import time

# Define metrics
report_generation_duration = Gauge('mtd_report_generation_seconds', 'Report generation duration')
report_generation_failed_total = Counter('mtd_report_generation_failed_total', 'Failed report generation count')

if __name__ == "__main__":
    # Start metrics server on port 8000
    start_http_server(8000)
    
    start_time = time.time()
    try:
        # Your code here
        pass
    except Exception as e:
        report_generation_failed_total.inc()
    finally:
        duration = time.time() - start_time
        report_generation_duration.set(duration)
```

### Email Notifications

Add to scheduling script:

```bash
# Send email on success
if [ $? -eq 0 ]; then
    echo "Report generated successfully" | \
    mail -s "✓ MTD Report Generated" team@example.com
fi

# Send email on failure
if [ $? -ne 0 ]; then
    echo "Report generation failed. Check logs." | \
    mail -s "✗ MTD Report Generation Failed" team@example.com
fi
```

### Slack Notifications

```python
import requests
import os

def send_slack_notification(status, message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return
    
    payload = {
        'text': f"MTD Report - {status}",
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f"*{status}*\n{message}"
                }
            }
        ]
    }
    
    requests.post(webhook_url, json=payload)

# In main.py:
try:
    report_df = generator.generate()
    send_slack_notification('✓ Success', 'Report generated successfully')
except Exception as e:
    send_slack_notification('✗ Failed', f'Error: {str(e)}')
```

---

## Troubleshooting

### Cron Job Not Running

1. **Check cron is enabled:**
   ```bash
   sudo systemctl status cron
   ```

2. **Verify environment variables:**
   - Cron runs in minimal environment
   - Specify full paths in scripts
   - Export necessary variables

3. **Check permissions:**
   ```bash
   ls -la /home/mtd-report/daily-report-automation-python/run_report.sh
   chmod +x /home/mtd-report/daily-report-automation-python/run_report.sh
   ```

4. **Test script directly:**
   ```bash
   /home/mtd-report/daily-report-automation-python/run_report.sh
   echo $?  # Should return 0 for success
   ```

### Windows Task Not Running

1. **Check Task History:**
   - Task Scheduler → Right-click task → View History

2. **Verify credentials:**
   - User account must have permission to access data files
   - Check user running the task

3. **Test batch file manually:**
   ```cmd
   C:\Applications\MTDReportAutomation\run_report.bat
   echo %ERRORLEVEL%
   ```

### Docker Container Issues

```bash
# Check container logs
docker logs <container_id>

# Enter running container
docker exec -it <container_id> /bin/bash

# Rebuild without cache
docker build --no-cache -t mtd-report:latest .
```

---

## Support & References

- [Cron Expression Generator](https://crontab.guru/)
- [Cron Format (Wikipedia)](https://en.wikipedia.org/wiki/Cron)
- [Windows Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/desktop/TaskSchd/task-scheduler-start-page)
- [Docker Documentation](https://docs.docker.com/)
- [Python Logging](https://docs.python.org/3/library/logging.html)

---

**Last Updated**: 2024
