"""
Configuration management for MTD Report Automation.

This module handles all configuration variables using environment variables
and default values. Centrizes config for easy management across environments.
"""

import os
from pathlib import Path
from typing import Optional

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class Config:
    """Configuration class for MTD Report Automation."""

    # File names
    MASTER_REPORT_FILE = os.getenv("MASTER_REPORT_FILE", "Master Report.xlsx")
    RETAILER_MAPPING_FILE = os.getenv("RETAILER_MAPPING_FILE", "retailer_rm_mapping.csv")
    BEAT_PLAN_FILE = os.getenv("BEAT_PLAN_FILE", "new_beat_plan.csv")

    # Input/Output paths
    DATA_INPUT_PATH = DATA_DIR
    OUTPUT_PATH = OUTPUT_DIR
    LOG_PATH = LOGS_DIR

    # Output file pattern
    OUTPUT_FILE_PATTERN = "MTD report {}.xlsx"  # {} will be replaced with date

    # Logging
    LOG_FILE_NAME = "mtd_report_automation.log"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Data processing
    DATE_FORMAT = "%Y-%m-%d"
    PERCENTAGE_DECIMAL_PLACES = 0
    SUNDAY_WEEKDAY = 6  # Python's weekday: 0=Monday, 6=Sunday

    # Columns expected in data
    MASTER_COLUMNS = ["RM code", "Distributor code"]
    RETAILER_MAPPING_COLUMNS = ["distributor_code", "rm_code", "retailer_code"]
    BEAT_PLAN_COLUMNS = ["uniquecode", "retailer_code", "date", "mark_as_done"]

    @classmethod
    def get_full_path(cls, filename: str, path_type: str = "data") -> Path:
        """
        Get full path to a file.

        Args:
            filename: Name of the file
            path_type: Type of path ('data', 'output', or 'log')

        Returns:
            Full path to the file
        """
        path_map = {"data": cls.DATA_INPUT_PATH, "output": cls.OUTPUT_PATH, "log": cls.LOG_PATH}
        return path_map.get(path_type, cls.DATA_INPUT_PATH) / filename

    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid
        """
        required_dirs = [cls.DATA_INPUT_PATH, cls.OUTPUT_PATH, cls.LOG_PATH]
        for dir_path in required_dirs:
            if not dir_path.exists():
                print(f"Warning: Directory {dir_path} does not exist. Creating it.")
                dir_path.mkdir(parents=True, exist_ok=True)
        return True
