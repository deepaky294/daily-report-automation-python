"""
Data processing logic for MTD Report Automation.

Handles data transformation, calculations, and business logic.
"""

import logging
from datetime import date, datetime
from typing import List

import numpy as np
import pandas as pd

from src.config import Config

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and transforms data for report generation."""

    @staticmethod
    def get_business_days_current_month() -> List[date]:
        """
        Calculate all business days in current month excluding Sundays.

        Returns:
            List of date objects for each business day
        """
        today = date.today()
        year = today.year
        month = today.month

        business_days = []
        for day in range(1, today.day + 1):
            current_date = date(year, month, day)
            # Exclude Sundays (weekday 6)
            if current_date.weekday() != Config.SUNDAY_WEEKDAY:
                business_days.append(current_date)

        logger.debug(f"Found {len(business_days)} business days in current month")
        return business_days

    @staticmethod
    def sync_rm_codes(
        master_df: pd.DataFrame, retailer_mapping_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Auto-sync RM codes from retailer mapping with master report.

        Args:
            master_df: Master report DataFrame
            retailer_mapping_df: Retailer-RM mapping DataFrame

        Returns:
            Updated master DataFrame with synced RM codes
        """
        logger.info("Syncing RM codes from retailer mapping...")

        if "distributor_code" not in retailer_mapping_df.columns or "rm_code" not in retailer_mapping_df.columns:
            logger.warning("Cannot sync RM codes - required columns not found")
            return master_df

        # Get unique distributor-RM mappings
        distributor_rm_mapping = retailer_mapping_df[["distributor_code", "rm_code"]].drop_duplicates()

        # Create list of expected RM codes for each distributor
        expected_rms = []
        for distributor in master_df["Distributor code"].unique():
            distributor_rms = distributor_rm_mapping[
                distributor_rm_mapping["distributor_code"] == distributor
            ]["rm_code"].tolist()

            for rm_code in distributor_rms:
                expected_rms.append(
                    {
                        "S.No.": "",
                        "Distributor code": distributor,
                        "RM code": rm_code,
                        "RM name": "",
                    }
                )

        expected_rm_df = pd.DataFrame(expected_rms)

        # Merge with existing master data
        if "RM name" in master_df.columns:
            master_df = pd.merge(
                expected_rm_df,
                master_df[["Distributor code", "RM code", "RM name"]],
                on=["Distributor code", "RM code"],
                how="left",
                suffixes=("", "_existing"),
            )
            master_df["RM name"] = master_df["RM name_existing"].combine_first(master_df["RM name"])
            master_df = master_df.drop("RM name_existing", axis=1)
        else:
            master_df = expected_rm_df

        # Auto-number S.No.
        master_df["S.No."] = range(1, len(master_df) + 1)

        logger.info(f"Synced RM codes. Total RMs: {len(master_df)}")
        return master_df

    @staticmethod
    def calculate_total_stores(
        master_df: pd.DataFrame, retailer_mapping_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate total stores for each RM.

        Args:
            master_df: Master DataFrame
            retailer_mapping_df: Retailer mapping DataFrame

        Returns:
            Master DataFrame with 'Total stores' column
        """
        logger.info("Calculating total stores...")

        store_counts = (
            retailer_mapping_df.groupby("rm_code")["retailer_code"]
            .nunique()
            .reset_index()
        )
        store_counts.columns = ["rm_code", "total_stores"]

        master_df = master_df.merge(
            store_counts, left_on="RM code", right_on="rm_code", how="left"
        )
        master_df["Total stores"] = master_df["total_stores"].fillna(0).astype(int)
        master_df.drop("total_stores", axis=1, inplace=True, errors="ignore")

        logger.debug(f"Total stores calculated for {len(master_df)} RMs")
        return master_df

    @staticmethod
    def calculate_unique_visits(
        master_df: pd.DataFrame, beat_plan_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate unique store visits till date for current month.

        Args:
            master_df: Master DataFrame
            beat_plan_df: Beat plan DataFrame

        Returns:
            Master DataFrame with 'Unique visit till date' column
        """
        logger.info("Calculating unique visits till date...")

        current_month = datetime.now().strftime("%Y-%m")
        current_month_visits = beat_plan_df[
            beat_plan_df["date"].str.startswith(current_month, na=False)
        ]

        unique_visits = (
            current_month_visits.groupby("uniquecode")["retailer_code"]
            .nunique()
            .reset_index()
        )
        unique_visits.columns = ["uniquecode", "unique_visits"]

        master_df = master_df.merge(
            unique_visits, left_on="RM code", right_on="uniquecode", how="left"
        )
        master_df["Unique visit till date"] = master_df["unique_visits"].fillna(0).astype(int)
        master_df.drop("unique_visits", axis=1, inplace=True, errors="ignore")

        return master_df

    @staticmethod
    def calculate_visit_percentage(master_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate unique visit percentage.

        Args:
            master_df: Master DataFrame with 'Total stores' and 'Unique visit till date'

        Returns:
            Master DataFrame with 'Unique visit %' column
        """
        logger.info("Calculating unique visit percentage...")

        master_df["Unique visit %"] = (
            np.where(
                master_df["Total stores"] > 0,
                np.round(
                    master_df["Unique visit till date"] / master_df["Total stores"] * 100
                ),
                0,
            )
            .astype(int)
            .astype(str)
            + "%"
        )

        return master_df

    @staticmethod
    def calculate_total_visits(
        master_df: pd.DataFrame, beat_plan_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate total visits (marked as done).

        Args:
            master_df: Master DataFrame
            beat_plan_df: Beat plan DataFrame

        Returns:
            Master DataFrame with 'Total visit' column
        """
        logger.info("Calculating total visits...")

        current_month = datetime.now().strftime("%Y-%m")
        current_month_visits = beat_plan_df[
            beat_plan_df["date"].str.startswith(current_month, na=False)
        ]
        done_visits = current_month_visits[current_month_visits["mark_as_done"] == "done"]

        total_visits = done_visits.groupby("uniquecode").size().reset_index()
        total_visits.columns = ["uniquecode", "total_visits_count"]

        master_df = master_df.merge(
            total_visits, left_on="RM code", right_on="uniquecode", how="left"
        )
        master_df["Total visit"] = master_df["total_visits_count"].fillna(0).astype(int)
        master_df.drop("total_visits_count", axis=1, inplace=True, errors="ignore")

        return master_df

    @staticmethod
    def calculate_average_counters_per_day(master_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate average counters per business day.

        Args:
            master_df: Master DataFrame with 'Total visit' column

        Returns:
            Master DataFrame with 'Average counters per day' column
        """
        logger.info("Calculating average counters per day...")

        business_days_count = len(DataProcessor.get_business_days_current_month())

        master_df["Average counters per day"] = (
            np.where(
                business_days_count > 0,
                np.round(master_df["Total visit"] / business_days_count),
                0,
            )
            .astype(int)
        )

        return master_df

    @staticmethod
    def add_daily_visit_columns(
        master_df: pd.DataFrame, beat_plan_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Add columns for each business day showing visit counts.

        Args:
            master_df: Master DataFrame
            beat_plan_df: Beat plan DataFrame

        Returns:
            Master DataFrame with daily columns
        """
        logger.info("Adding daily visit columns...")

        current_month = datetime.now().strftime("%Y-%m")
        done_visits_current_month = beat_plan_df[
            (beat_plan_df["mark_as_done"] == "done")
            & (beat_plan_df["date"].str.startswith(current_month, na=False))
        ]

        business_days_list = DataProcessor.get_business_days_current_month()

        # Create temporary dataframe for daily counts
        daily_counts_df = pd.DataFrame()
        daily_counts_df["RM code"] = master_df["RM code"]

        # Process each business day
        for business_day in business_days_list:
            col_name = business_day.strftime("%d-%b")
            date_str = business_day.strftime("%Y-%m-%d")

            day_visits = done_visits_current_month[
                done_visits_current_month["date"] == date_str
            ]

            day_visit_counts = day_visits.groupby("uniquecode").size().reset_index()
            day_visit_counts.columns = ["RM code", col_name]

            daily_counts_df = daily_counts_df.merge(
                day_visit_counts, on="RM code", how="left"
            )
            daily_counts_df[col_name] = daily_counts_df[col_name].fillna(0).astype(int)

        # Merge all daily columns with master dataframe
        master_df = master_df.merge(daily_counts_df, on="RM code", how="left")

        logger.info(
            f"Added {len(business_days_list)} daily columns: "
            f"{[day.strftime('%d-%b') for day in business_days_list]}"
        )
        return master_df

    @staticmethod
    def reorder_columns(master_df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorder columns in the report.

        Args:
            master_df: Master DataFrame

        Returns:
            DataFrame with reordered columns
        """
        column_order = [
            "S.No.",
            "Distributor code",
            "RM code",
            "RM name",
            "Total stores",
            "Unique visit till date",
            "Unique visit %",
            "Total visit",
            "Average counters per day",
        ]

        # Add daily columns after main columns
        daily_columns = [col for col in master_df.columns if col not in column_order]
        final_column_order = column_order + daily_columns

        master_df = master_df[final_column_order]
        logger.debug(f"Reordered columns. Final count: {len(master_df.columns)}")
        return master_df
