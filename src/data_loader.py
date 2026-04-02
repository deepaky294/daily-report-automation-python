"""
Data loading utilities for MTD Report Automation.

Handles loading data from Excel and CSV files with error handling
and validation.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from src.config import Config

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads and validates data from various file formats."""

    @staticmethod
    def load_excel(file_path: Path, sheet_name: int = 0) -> Optional[pd.DataFrame]:
        """
        Load data from an Excel file.

        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet name or index (default: first sheet)

        Returns:
            DataFrame if successful, None otherwise

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be read
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"Successfully loaded Excel file: {file_path}")
            logger.debug(f"Shape: {df.shape}, Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {str(e)}")
            raise ValueError(f"Failed to read Excel file: {str(e)}")

    @staticmethod
    def load_csv(file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load data from a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            DataFrame if successful, None otherwise

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be read
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded CSV file: {file_path}")
            logger.debug(f"Shape: {df.shape}, Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            raise ValueError(f"Failed to read CSV file: {str(e)}")

    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: list) -> bool:
        """
        Validate that DataFrame has all required columns.

        Args:
            df: DataFrame to validate
            required_columns: List of required column names

        Returns:
            True if all columns exist

        Raises:
            ValueError: If any required columns are missing
        """
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.error(
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {list(df.columns)}"
            )
            raise ValueError(f"Missing required columns: {missing_columns}")

        logger.debug(f"Column validation passed for {len(required_columns)} columns")
        return True

    @staticmethod
    def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        """
        Rename DataFrame columns using a mapping dictionary.

        Args:
            df: DataFrame to modify
            mapping: Dictionary of old_name -> new_name

        Returns:
            DataFrame with renamed columns
        """
        df = df.rename(columns=mapping)
        logger.debug(f"Renamed {len(mapping)} columns")
        return df

    @staticmethod
    def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Create sample data for demonstration/testing.

        Returns:
            Tuple of (master_df, retailer_mapping_df, beat_plan_df)
        """
        from datetime import datetime

        current_month = datetime.now().strftime("%Y-%m")

        master_df = pd.DataFrame(
            {
                "S.No.": [1, 2, 3],
                "Distributor code": ["DIST_125", "DIST_125", "DIST_126"],
                "RM code": ["RM_375", "RM_376", "RM_378"],
                "RM name": ["RM A", "RM B", "RM C"],
            }
        )

        retailer_mapping_df = pd.DataFrame(
            {
                "distributor_code": ["DIST_125", "DIST_125", "DIST_125", "DIST_126", "DIST_126"],
                "rm_code": ["RM_375", "RM_376", "RM_376", "RM_378", "RM_378"],
                "retailer_code": ["RET_378", "RET_376", "RET_377", "RET_378", "RET_379"],
            }
        )

        beat_plan_df = pd.DataFrame(
            {
                "uniquecode": ["RM_375", "RM_375", "RM_375", "RM_376", "RM_376"],
                "retailer_code": ["RET_378", "RET_376", "RET_377", "RET_378", "RET_379"],
                "date": [
                    f"{current_month}-01",
                    f"{current_month}-02",
                    f"{current_month}-03",
                    f"{current_month}-01",
                    f"{current_month}-02",
                ],
                "mark_as_done": ["done", "done", "done", "done", "done"],
            }
        )

        logger.info("Created sample data for demonstration")
        return master_df, retailer_mapping_df, beat_plan_df
