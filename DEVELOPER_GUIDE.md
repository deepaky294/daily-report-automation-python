# Developer Quick Reference

Quick reference guide for developers working on this project.

## Project Structure

```
src/                          # Source code
├── config.py                 # Configuration & constants
├── logger.py                 # Logging setup
├── data_loader.py            # Load & validate data
├── data_processor.py         # Data transformation
└── report_generator.py       # Main orchestration

main.py                       # Entry point
requirements.txt              # Dependencies
```

## Common Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running
```bash
# Run locally
python main.py

# Debug mode
LOG_LEVEL=DEBUG python main.py

# With custom config
MASTER_REPORT_FILE="custom.xlsx" python main.py

# Docker
docker-compose up --build
docker-compose down
```

### Scheduling
```bash
# Linux/macOS - Edit crontab
crontab -e

# Windows - Use Task Scheduler GUI
# Program: C:\path\to\run_report.bat
```

### Debugging
```bash
# Check logs
tail -f logs/mtd_report_automation.log

# Enable verbose logging
LOG_LEVEL=DEBUG python main.py 2>&1 | tee debug.log
```

## Key Classes

### ReportGenerator
Main orchestrator class in `src/report_generator.py`

```python
from src.report_generator import ReportGenerator

generator = ReportGenerator()
df = generator.generate()  # Returns DataFrame with report
```

### DataProcessor
Data transformation in `src/data_processor.py`

```python
from src.data_processor import DataProcessor

processor = DataProcessor()
business_days = processor.get_business_days_current_month()
df = processor.calculate_total_stores(master_df, retailer_df)
```

### DataLoader
File loading in `src/data_loader.py`

```python
from src.data_loader import DataLoader

loader = DataLoader()
df = loader.load_excel(file_path)
df = loader.load_csv(file_path)
loader.validate_columns(df, ['col1', 'col2'])
```

## Configuration

Edit `src/config.py` to change:
- File names: `MASTER_REPORT_FILE`, `RETAILER_MAPPING_FILE`, etc.
- Directories: `DATA_DIR`, `OUTPUT_DIR`, `LOGS_DIR`
- Logging: `LOG_LEVEL`, `LOG_FILE_NAME`
- Data specs: `MASTER_COLUMNS`, `BEAT_PLAN_COLUMNS`

Or use environment variables:
```bash
export LOG_LEVEL=DEBUG
export MASTER_REPORT_FILE="Custom Report.xlsx"
```

## Adding Features

### 1. Add a new calculation
**File:** `src/data_processor.py`

```python
class DataProcessor:
    @staticmethod
    def calculate_my_metric(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate my custom metric."""
        df['my_metric'] = df['col1'] + df['col2']
        logger.info("Calculated my_metric")
        return df
```

**Then use in:** `src/report_generator.py`

```python
master_df = self.processor.calculate_my_metric(master_df)
```

### 2. Add a new file format
**File:** `src/data_loader.py`

```python
@staticmethod
def load_json(file_path: Path) -> Optional[pd.DataFrame]:
    """Load JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_json(file_path)
        logger.info(f"Loaded JSON: {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        raise
```

### 3. Add error notifications
**File:** `main.py`

```python
import smtplib

def send_error_email(error_message):
    """Send error notification."""
    # Implementation here
    pass

try:
    report_df = generator.generate()
except Exception as e:
    send_error_email(str(e))
    raise
```

## Testing Examples

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

**Test file:** `tests/test_data_processor.py`

```python
import pytest
from src.data_processor import DataProcessor
import pandas as pd

def test_calculate_total_stores():
    processor = DataProcessor()
    
    # Create test data
    master_df = pd.DataFrame({
        'RM code': ['RM_1', 'RM_2'],
        'Distributor code': ['D1', 'D1']
    })
    
    retailer_df = pd.DataFrame({
        'rm_code': ['RM_1', 'RM_1', 'RM_2'],
        'retailer_code': ['R1', 'R2', 'R3']
    })
    
    # Call function
    result = processor.calculate_total_stores(master_df, retailer_df)
    
    # Assert
    assert 'Total stores' in result.columns
    assert result[result['RM code'] == 'RM_1']['Total stores'].values[0] == 2
```

## Performance Tips

1. **For large datasets:**
   ```python
   # Use chunking
   for chunk in pd.read_csv(file, chunksize=10000):
       process_chunk(chunk)
   ```

2. **Profile for bottlenecks:**
   ```bash
   python -m cProfile -s cumulative main.py | head -20
   ```

3. **Use appropriate data types:**
   ```python
   df['id'] = df['id'].astype('int32')  # Not 'object'
   ```

## Logging Best Practices

```python
from src.logger import setup_logger
logger = setup_logger(__name__)

# Different log levels
logger.debug("Detailed debugging info")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

## Deployment Checklist

- [ ] Update version in `src/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run all tests: `pytest`
- [ ] Check code quality: `flake8 src/ main.py`
- [ ] Update README.md if needed
- [ ] Tag release: `git tag -a v1.0.0 -m "Release 1.0.0"`
- [ ] Push to production

## Troubleshooting

### Import errors
```bash
# Reinstall package
pip install -e .  # If using setup.py
# OR
python -m pip install --upgrade pip
```

### Permission denied
```bash
chmod +x run_report.sh  # Linux/macOS
```

### Port already in use
```bash
docker-compose down  # Stop containers
```

### File not found
```bash
# Check file exists
ls -la data/
# Check config
LOG_LEVEL=DEBUG python main.py
```

## Resources

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Docker Documentation](https://docs.docker.com/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Type Hints](https://docs.python.org/3/library/typing.html)

## Contact & Support

For issues or questions:
1. Check the logs: `logs/mtd_report_automation.log`
2. Enable debug mode: `LOG_LEVEL=DEBUG python main.py`
3. Review [README.md](README.md)
4. See [DEPLOYMENT.md](DEPLOYMENT.md)
