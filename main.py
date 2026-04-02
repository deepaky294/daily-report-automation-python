#!/usr/bin/env python3
"""
Main entry point for MTD Report Automation.

Usage:
    python main.py

Environment variables:
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    MASTER_REPORT_FILE: Name of the master report file
    RETAILER_MAPPING_FILE: Name of the retailer mapping CSV file
    BEAT_PLAN_FILE: Name of the beat plan CSV file
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.logger import setup_logger
from src.report_generator import ReportGenerator

logger = setup_logger(__name__)


def main():
    """Main execution function."""
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Config.validate()

        # Initialize report generator
        generator = ReportGenerator()

        # Generate report
        report_df = generator.generate()

        if report_df is not None:
            logger.info("✓ Report generation completed successfully!")
            return 0
        else:
            logger.error("✗ Report generation failed")
            return 1

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
