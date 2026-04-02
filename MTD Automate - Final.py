import pandas as pd
import numpy as np
from datetime import datetime, date
import calendar
import warnings
import os
warnings.filterwarnings('ignore')

def get_business_days_current_month():
    """Calculate all business days in current month excluding Sundays"""
    today = date.today()
    year = today.year
    month = today.month
    
    # Get all business days from 1st to today (excluding Sundays)
    business_days = []
    for day in range(1, today.day + 1):
        current_date = date(year, month, day)
        if current_date.weekday() != 6:  # Sunday is 6
            business_days.append(current_date)
    
    return business_days

def generate_master_report():
    """
    Generate automated master report based on the requirements
    Uses 'Master Report.xlsx' from the same directory as the script
    Uses CSV files for retailer_rm_mapping and new_beat_plan
    """
    
    # Get the current directory where the script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))
    master_file_path = os.path.join(current_directory, "Master Report.xlsx")
    
    # Check if Master Report.xlsx exists
    if not os.path.exists(master_file_path):
        print(f"Error: 'Master Report.xlsx' not found in the directory: {current_directory}")
        print("Please make sure the file exists in the same folder as this script.")
        return None
    
    # Read master file
    try:
        master_df = pd.read_excel(master_file_path)
        print("Master Report.xlsx loaded successfully")
        
        # Debug: Show column names to help identify the correct ones
        print("Columns found in Master Report.xlsx:")
        for col in master_df.columns:
            print(f"  - '{col}'")
            
    except Exception as e:
        print(f"Error loading Master Report.xlsx: {e}")
        return None
    
    # Check if required columns exist
    required_columns = ['RM code', 'Distributor code']  # These are the critical columns
    missing_columns = [col for col in required_columns if col not in master_df.columns]
    
    if missing_columns:
        print(f"\nError: The following required columns are missing: {missing_columns}")
        print("Please check your Master Report.xlsx file and update the column names.")
        print("Available columns are:", list(master_df.columns))
        return None
    
    # Look for CSV data files in the same directory
    print("\nSetting up data sources from CSV files...")
    
    retailer_file = os.path.join(current_directory, "retailer_rm_mapping.csv")
    beat_plan_file = os.path.join(current_directory, "new_beat_plan.csv")
    
    # Try to load from CSV files
    try:
        if os.path.exists(retailer_file):
            retailer_rm_mapping = pd.read_csv(retailer_file)
            print("Loaded retailer_rm_mapping from CSV file")
            print(f"Columns in retailer_rm_mapping: {list(retailer_rm_mapping.columns)}")
        else:
            # Create sample data for demonstration
            print("Creating sample retailer data for demonstration...")
            retailer_rm_mapping = pd.DataFrame({
                'distributor_code': ['DIST_125', 'DIST_125', 'DIST_125', 'DIST_126', 'DIST_126'],
                'rm_code': ['RM_375', 'RM_376', 'RM_377', 'RM_378', 'RM_379'],
                'retailer_code': ['RET_378', 'RET_376', 'RET_377', 'RET_378', 'RET_379']
            })
            
    except Exception as e:
        print(f"Error loading retailer data: {e}")
        return None
    
    try:
        if os.path.exists(beat_plan_file):
            new_beat_plan = pd.read_csv(beat_plan_file)
            print("Loaded new_beat_plan from CSV file")
            print(f"Columns in new_beat_plan: {list(new_beat_plan.columns)}")
            
            # Convert date to string for filtering if it's not already
            if 'date' in new_beat_plan.columns:
                new_beat_plan['date'] = new_beat_plan['date'].astype(str)
        else:
            # Create sample data for demonstration
            print("Creating sample beat plan data for demonstration...")
            current_month = datetime.now().strftime('%Y-%m')
            new_beat_plan = pd.DataFrame({
                'uniquecode': ['RM_375', 'RM_375', 'RM_375', 'RM_375', 'RM_376', 'RM_376', 'RM_375'],
                'retailer_code': ['RET_378', 'RET_376', 'RET_377', 'RET_378', 'RET_379', 'RET_380', 'RET_376'],
                'date': [f'{current_month}-01', f'{current_month}-02', f'{current_month}-03', 
                        f'{current_month}-04', f'{current_month}-01', f'{current_month}-02',
                        f'{current_month}-05'],
                'mark_as_done': ['done', 'done', 'done', 'done', 'done', 'done', 'done']
            })
            
    except Exception as e:
        print(f"Error loading beat plan data: {e}")
        return None
    
    # NEW: Auto-sync RM codes from retailer_rm_mapping with Master Report
    print("\nSyncing RM codes from retailer_rm_mapping...")
    
    # Get unique distributor-RM mappings from retailer_rm_mapping
    if 'distributor_code' in retailer_rm_mapping.columns and 'rm_code' in retailer_rm_mapping.columns:
        distributor_rm_mapping = retailer_rm_mapping[['distributor_code', 'rm_code']].drop_duplicates()
        
        # Create a list of all expected RM codes for each distributor
        expected_rms = []
        for distributor in master_df['Distributor code'].unique():
            distributor_rms = distributor_rm_mapping[
                distributor_rm_mapping['distributor_code'] == distributor
            ]['rm_code'].tolist()
            
            for rm_code in distributor_rms:
                expected_rms.append({
                    'S.No.': '',  # Will be auto-numbered later
                    'Distributor code': distributor,
                    'RM code': rm_code,
                    'RM name': ''  # Blank for new RMs
                })
        
        # Create expected RM dataframe
        expected_rm_df = pd.DataFrame(expected_rms)
        
        # Merge with existing master data to preserve RM names for existing RMs
        if 'RM name' in master_df.columns:
            # Keep existing RM names where available
            master_df = pd.merge(
                expected_rm_df, 
                master_df[['Distributor code', 'RM code', 'RM name']], 
                on=['Distributor code', 'RM code'], 
                how='left',
                suffixes=('', '_existing')
            )
            
            # Combine RM names (prefer existing ones, use new blank ones for new RMs)
            master_df['RM name'] = master_df['RM name_existing'].combine_first(master_df['RM name'])
            master_df = master_df.drop('RM name_existing', axis=1)
        else:
            master_df = expected_rm_df
        
        # Auto-number S.No.
        master_df['S.No.'] = range(1, len(master_df) + 1)
        
        print(f"Synced RM codes. Total RMs in report: {len(master_df)}")
        print(f"Distributors found: {master_df['Distributor code'].nunique()}")
    else:
        print("Warning: Could not sync RM codes - required columns not found in retailer_rm_mapping")
    
    # Calculate Column E: Total stores
    print("\nCalculating Total stores...")
    store_counts = retailer_rm_mapping.groupby('rm_code')['retailer_code'].nunique().reset_index()
    store_counts.columns = ['rm_code', 'total_stores']
    master_df = master_df.merge(store_counts, left_on='RM code', right_on='rm_code', how='left')
    master_df['Total stores'] = master_df['total_stores'].fillna(0).astype(int)
    
    # Calculate Column F: Unique visit till date
    print("Calculating Unique visit till date...")
    current_month = datetime.now().strftime('%Y-%m')
    
    # Filter for current month visits
    current_month_visits = new_beat_plan[
        new_beat_plan['date'].str.startswith(current_month, na=False)
    ]
    
    unique_visits = current_month_visits.groupby('uniquecode')['retailer_code'].nunique().reset_index()
    unique_visits.columns = ['uniquecode', 'unique_visits']
    master_df = master_df.merge(unique_visits, left_on='RM code', right_on='uniquecode', how='left')
    master_df['Unique visit till date'] = master_df['unique_visits'].fillna(0).astype(int)
    
    # Calculate Column G: Unique visit % (rounded to nearest whole percentage)
    print("Calculating Unique visit %...")
    master_df['Unique visit %'] = np.where(
        master_df['Total stores'] > 0,
        round(master_df['Unique visit till date'] / master_df['Total stores'] * 100),
        0
    ).astype(int).astype(str) + '%'
    
    # Calculate Column H: Total visit
    print("Calculating Total visit...")
    done_visits = current_month_visits[current_month_visits['mark_as_done'] == 'done']
    total_visits = done_visits.groupby('uniquecode').size().reset_index()
    total_visits.columns = ['uniquecode', 'total_visits_count']
    master_df = master_df.merge(total_visits, left_on='RM code', right_on='uniquecode', how='left')
    master_df['Total visit'] = master_df['total_visits_count'].fillna(0).astype(int)
    
    # Calculate Column I: Average counters per day (rounded to nearest whole number)
    print("Calculating Average counters per day...")
    business_days_list = get_business_days_current_month()
    business_days_count = len(business_days_list)
    master_df['Average counters per day'] = np.where(
        business_days_count > 0,
        round(master_df['Total visit'] / business_days_count),
        0
    ).astype(int)
    
    # Add dynamic date columns for each business day
    print("\nAdding daily visit columns...")
    
    # Filter for done visits in current month
    done_visits_current_month = new_beat_plan[
        (new_beat_plan['mark_as_done'] == 'done') & 
        (new_beat_plan['date'].str.startswith(current_month, na=False))
    ]
    
    # Create a temporary dataframe for daily counts to avoid multiple merges
    daily_counts_df = pd.DataFrame()
    daily_counts_df['RM code'] = master_df['RM code']
    
    # Process each business day
    for business_day in business_days_list:
        # Format column name as "DD-MMM" (e.g., "17-Nov")
        col_name = business_day.strftime("%d-%b")
        
        # Format the date for comparison (YYYY-MM-DD)
        date_str = business_day.strftime("%Y-%m-%d")
        
        # Filter visits for this specific date
        day_visits = done_visits_current_month[
            done_visits_current_month['date'] == date_str
        ]
        
        # Count visits per RM for this day
        day_visit_counts = day_visits.groupby('uniquecode').size().reset_index()
        day_visit_counts.columns = ['RM code', col_name]
        
        # Merge with temporary dataframe
        daily_counts_df = daily_counts_df.merge(day_visit_counts, on='RM code', how='left')
        daily_counts_df[col_name] = daily_counts_df[col_name].fillna(0).astype(int)
    
    # Merge all daily columns with master dataframe at once
    master_df = master_df.merge(daily_counts_df, on='RM code', how='left')
    
    print(f"Added {len(business_days_list)} daily columns: {[day.strftime('%d-%b') for day in business_days_list]}")
    
    # Clean up all temporary columns
    columns_to_drop = ['total_stores', 'unique_visits', 'total_visits_count', 'rm_code', 'uniquecode']
    master_df.drop(columns_to_drop, axis=1, inplace=True, errors='ignore')
    
    # Reorder columns to maintain original structure
    column_order = ['S.No.', 'Distributor code', 'RM code', 'RM name', 
                   'Total stores', 'Unique visit till date', 'Unique visit %', 
                   'Total visit', 'Average counters per day']
    
    # Add daily columns after the main columns
    daily_columns = [col for col in master_df.columns if col not in column_order]
    final_column_order = column_order + daily_columns
    
    master_df = master_df[final_column_order]
    
    # Save the file with name "MTD report" and current date in the same directory
    current_date = datetime.now().strftime("%d-%m-%Y")
    output_file = f"MTD report {current_date}.xlsx"
    output_file_path = os.path.join(current_directory, output_file)
    
    master_df.to_excel(output_file_path, index=False)
    print(f"\nReport generated successfully and saved as: {output_file_path}")
    print(f"Total columns in report: {len(master_df.columns)}")
    print(f"Total RMs by distributor:")
    rm_counts = master_df['Distributor code'].value_counts()
    for distributor, count in rm_counts.items():
        print(f"  - {distributor}: {count} RMs")
    
    return master_df

# Example usage
if __name__ == "__main__":
    # Generate the report - no parameters needed
    print("Starting MTD Report Generation...")
    print("Looking for 'Master Report.xlsx' in the same directory...")
    print("Also looking for 'retailer_rm_mapping.csv' and 'new_beat_plan.csv' files...")
    
    result_df = generate_master_report()
    
    # Display sample of the results
    if result_df is not None:
        print("\nSample of generated report:")
        print(result_df.head())
        
        print(f"\nReport completed successfully!")
        print(f"Total RMs processed: {len(result_df)}")
        print(f"Total columns in output: {len(result_df.columns)}")
        
        # Show summary statistics
        print(f"\nSummary Statistics:")
        print(f"Total stores covered: {result_df['Total stores'].sum()}")
        print(f"Total unique visits: {result_df['Unique visit till date'].sum()}")
        print(f"Total visits: {result_df['Total visit'].sum()}")
    else:
        print("\nReport generation failed. Please check the error messages above.")
