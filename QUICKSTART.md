# Quick Start Guide

Get up and running with MTD Report Automation in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/daily-report-automation-python.git
cd daily-report-automation-python
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Sample Data

Copy your data files to the `data/` directory:
- `Master Report.xlsx`
- `retailer_rm_mapping.csv`
- `new_beat_plan.csv`

**Don't have data files yet?** The script will create sample data automatically on first run.

### 5. Run the Report Generator

```bash
python main.py
```

### 6. Check Your Report

Reports are generated in the `output/` directory with the format:
```
output/MTD report DD-MM-YYYY.xlsx
```

Logs are available in:
```
logs/mtd_report_automation.log
```

## Next Steps

- 📚 Read the full [README.md](README.md) for complete documentation
- 🚀 Set up scheduling in [DEPLOYMENT.md](DEPLOYMENT.md)
- ⚙️ Customize configuration in [src/config.py](src/config.py)
- 🐳 Use Docker: `docker-compose up --build`

## Troubleshooting

**Module not found errors:**
```bash
pip install -r requirements.txt  # Reinstall dependencies
```

**Permission denied on run_report.sh:**
```bash
chmod +x run_report.sh  # Make it executable
```

**PowerShell execution policy (Windows):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

For more help, see [README.md - Troubleshooting](README.md#troubleshooting).
