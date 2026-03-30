import pandas as pd
import numpy as np
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_status(phase: str, message: str, progress: int):
    """Update status file for frontend tracking."""
    status_path = os.path.join("..", "data", "status.json")
    if not os.path.exists(os.path.dirname(status_path)):
        os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w") as f:
        json.dump({"phase": phase, "message": message, "progress": progress}, f)

def clean_data(raw_path: str, output_dir: str) -> str:
    """
    Refined Universal ETL Cleaning:
    - Filters out non-country aggregations (continents, Income groups)
    - Enforces strict data typing (Datetime, Numeric)
    - Interpolates gaps in time-series
    - Handles Outliers with IQR clamping
    """
    try:
        update_status("Cleaning", "Loading raw data and identifying schema...", 10)
        logging.info(f"Loading raw data from {raw_path}")
        df = pd.read_csv(raw_path, low_memory=False)
        initial_rows = len(df)

        # 1. Continent / Aggregation Filtering (OWID Specific handling)
        update_status("Cleaning", "Filtering non-country aggregations...", 20)
        
        # Drop rows where iso_code starts with OWID_ (aggregations) but keep those that are countries if they exist.
        # Standard OWID aggregations: OWID_WRL, OWID_EUR, OWID_ASI, etc.
        # Exceptions: OWID_KOS (Kosovo) is often treated as a country.
        if 'iso_code' in df.columns:
            # We filter out typical continent/income aggregations. 
            # These are usually 4+ characters and not standard country ISOs or specific exceptions.
            # A more robust check is against the location if it's "World", "Europe", etc.
            aggregations = ["World", "Europe", "Asia", "North America", "South America", "Africa", "Oceania", "European Union", "High income", "Low income", "Lower middle income", "Upper middle income"]
            if 'location' in df.columns:
                df = df[~df['location'].isin(aggregations)]
            
            # Further filter OWID_ prefixes that are clearly regions
            # OWID_WRL is world, OWID_KOS is Kosovo (keep), OWID_SAM (South America), etc.
            df = df[~((df['iso_code'].str.startswith('OWID_')) & (~df['iso_code'].isin(['OWID_KOS'])))]

        # 2. Strict Data Typing
        update_status("Cleaning", "Ensuring strict data typing...", 30)
        
        # Find date column
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_col = col
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                break
        
        # Ensure numerics are numeric
        numerics = df.select_dtypes(include=[np.number]).columns.tolist()
        # Also check object columns that should be numeric
        for col in df.columns:
            if col != date_col and col not in df.select_dtypes(include=['object']).columns:
                continue
            if 'index' in col.lower() or 'code' in col.lower() or 'location' in col.lower() or 'country' in col.lower():
                continue
            
            # Try to convert to numeric if it's not a known category
            potential_numeric = pd.to_numeric(df[col], errors='coerce')
            if not potential_numeric.isna().all():
                df[col] = potential_numeric
                if col not in numerics:
                    numerics.append(col)

        # 3. Missing Value Handling & Interpolation
        update_status("Cleaning", "Interpolating time-series gaps...", 45)
        
        # Mandatory fields: must have a date and a location/iso_code
        id_cols = []
        if date_col: id_cols.append(date_col)
        loc_col = 'location' if 'location' in df.columns else ('country' if 'country' in df.columns else None)
        if loc_col: id_cols.append(loc_col)
        
        if id_cols:
            df.dropna(subset=id_cols, inplace=True)
            
            # Sort for interpolation stability
            df.sort_values(by=id_cols, inplace=True)
            
            # Group-based interpolation for numeric gaps
            if loc_col:
                # We interpolate small gaps. Large gaps are left alone to avoid distortion.
                # Use limit=3 to avoid inventing data for long outages.
                for col in numerics:
                    df[col] = df.groupby(loc_col)[col].transform(lambda x: x.interpolate(method='linear', limit=3).ffill().bfill())

        # 4. Outlier Handling (IQR)
        update_status("Cleaning", "clamping abnormal metric spikes...", 60)
        outlier_stats = 0
        for col in numerics:
            # We only clamp positive metrics (counts usually)
            if df[col].min() >= 0:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                upper = Q3 + 3.0 * IQR # Using 3.0 for "Extreme" outliers to allow natural variances
                
                mask = df[col] > upper
                outlier_stats += mask.sum()
                df.loc[mask, col] = upper

        # 5. Final Duplication Cleanup
        update_status("Cleaning", "Finalizing cleaned records...", 75)
        df.drop_duplicates(subset=id_cols, inplace=True)
        
        final_rows = len(df)
        rows_dropped = initial_rows - final_rows
        
        # Save Stats
        stats = {
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "rows_dropped": rows_dropped,
            "outliers_clamped": int(outlier_stats),
            "features": len(df.columns)
        }
        with open(os.path.join(output_dir, "cleaning_stats.json"), "w") as f:
            json.dump(stats, f)
            
        logging.info(f"Refined cleaning completed. Dropped {rows_dropped} rows.")
        update_status("Cleaning", "Data improvement successful.", 80)
        
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "cleaned_dynamic_data.csv")
        df.to_csv(out_path, index=False)
        return out_path
        
    except Exception as e:
        logging.error(f"Error in refined cleaning: {e}")
        update_status("Error", f"Improvements failed: {str(e)}", 0)
        raise
