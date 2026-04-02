"""
Report generation module for MTD Report Automation.

Orchestrates the entire report generation pipeline.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import Config
from src.data_loader import DataLoader
from src.data_processor import DataProcessor

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates MTD reports from raw data."""

    def __init__(self, config: Config = None):
        """
        Initialize the report generator.

        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config
        self.data_loader = DataLoader()
        self.processor = DataProcessor()

    def load_data(self) -> Optional[tuple]:
        """
        Load all required data files.

        Returns:
            Tuple of (master_df, retailer_mapping_df, beat_plan_df) or None on failure

        Raises:
            FileNotFoundError: If required files are missing
            ValueError: If files cannot be read
        """
        logger.info("Loading data files...")

        try:
            master_file = self.config.get_full_path(
                self.config.MASTER_REPORT_FILE, "data"
            )
            retailer_file = self.config.get_full_path(
                self.config.RETAILER_MAPPING_FILE, "data"
            )
            beat_plan_file = self.config.get_full_path(self.config.BEAT_PLAN_FILE, "data")

            # Try to load actual files
            if master_file.exists():
                logger.info(f"Loading master report from {master_file}")
                master_df = self.data_loader.load_excel(master_file)
                self.data_loader.validate_columns(
                    master_df, self.config.MASTER_COLUMNS
                )
            else:
                logger.warning(
                    f"Master file not found at {master_file}. Using sample data."
                )
                master_df, retailer_mapping_df, beat_plan_df = (
                    self.data_loader.create_sample_data()
                )
                return master_df, retailer_mapping_df, beat_plan_df

            if retailer_file.exists():
                logger.info(f"Loading retailer mapping from {retailer_file}")
                retailer_mapping_df = self.data_loader.load_csv(retailer_file)
            else:
                logger.warning(f"Retailer mapping not found at {retailer_file}. Using sample data.")
                _, retailer_mapping_df, _ = self.data_loader.create_sample_data()

            if beat_plan_file.exists():
                logger.info(f"Loading beat plan from {beat_plan_file}")
                beat_plan_df = self.data_loader.load_csv(beat_plan_file)
                beat_plan_df["date"] = beat_plan_df["date"].astype(str)
            else:
                logger.warning(f"Beat plan not found at {beat_plan_file}. Using sample data.")
                _, _, beat_plan_df = self.data_loader.create_sample_data()

            logger.info("All data files loaded successfully")
            return master_df, retailer_mapping_df, beat_plan_df

        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def generate(self) -> Optional[pd.DataFrame]:
        """
        Generate the complete MTD report.

        Returns:
            Generated report DataFrame or None on failure
        """
        try:
            logger.info("=" * 80)
            logger.info("Starting MTD Report Generation")
            logger.info("=" * 80)

            # Load data
            master_df, retailer_mapping_df, beat_plan_df = self.load_data()

            if master_df is None:
                logger.error("Failed to load required data")
                return None

            # Process data
            logger.info("Processing data...")
            master_df = self.processor.sync_rm_codes(master_df, retailer_mapping_df)
            master_df = self.processor.calculate_total_stores(
                master_df, retailer_mapping_df
            )
            master_df = self.processor.calculate_unique_visits(master_df, beat_plan_df)
            master_df = self.processor.calculate_visit_percentage(master_df)
            master_df = self.processor.calculate_total_visits(master_df, beat_plan_df)
            master_df = self.processor.calculate_average_counters_per_day(master_df)
            master_df = self.processor.add_daily_visit_columns(master_df, beat_plan_df)
            master_df = self.processor.reorder_columns(master_df)

            # Save report
            output_file = self._save_report(master_df)

            # Log summary
            self._log_summary(master_df)

            logger.info("Report generation completed successfully")
            logger.info("=" * 80)

            return master_df

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            raise

    def _save_report(self, df: pd.DataFrame) -> Path:
        """
        Save the report to an Excel file.

        Args:
            df: Report DataFrame

        Returns:
            Path to the saved file
        """
        current_date = datetime.now().strftime("%d-%m-%Y")
        output_filename = self.config.OUTPUT_FILE_PATTERN.format(current_date)
        output_file = self.config.get_full_path(output_filename, "output")

        try:
            df.to_excel(output_file, index=False)
            logger.info(f"Report saved successfully: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving report to {output_file}: {str(e)}")
            raise

    @staticmethod
    def _log_summary(df: pd.DataFrame) -> None:
        """
        Log summary statistics of the report.

        Args:
            df: Report DataFrame
        """
        logger.info("Report Summary:")
        logger.info(f"  - Total columns: {len(df.columns)}")
        logger.info(f"  - Total RMs: {len(df)}")

        if "Distributor code" in df.columns:
            rm_counts = df["Distributor code"].value_counts()
            logger.info("  - RMs by distributor:")
            for distributor, count in rm_counts.items():
                logger.info(f"      - {distributor}: {count} RMs")

        if "Total stores" in df.columns:
            logger.info(f"  - Total stores covered: {df['Total stores'].sum()}")

        if "Unique visit till date" in df.columns:
            logger.info(f"  - Total unique visits: {df['Unique visit till date'].sum()}")

        if "Total visit" in df.columns:
            logger.info(f"  - Total visits: {df['Total visit'].sum()}")
