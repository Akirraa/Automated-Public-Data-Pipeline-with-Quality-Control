import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_data(raw_path: str, output_dir: str) -> str:
    """
    Cleans any generic CSV: dynamically imputes nulls, handles datatypes.
    """
    try:
        logging.info(f"Loading raw data from {raw_path}")
        df = pd.read_csv(raw_path, low_memory=False)
        initial_rows = len(df)
        
        # Universal Cleaning
        df.dropna(how='all', inplace=True)
        
        # Auto-detect numerics
        numerics = df.select_dtypes(include=['number']).columns
        for col in numerics:
            # Impute with mean to ensure continuous curves for Auto-ETL rendering
            mean_val = df[col].mean()
            if pd.isna(mean_val):
                mean_val = 0
            df[col] = df[col].fillna(mean_val) 
            df.loc[df[col] < 0, col] = 0 # Generic count clamping
            
        # Auto-detect categoricals
        categoricals = df.select_dtypes(include=['object', 'category']).columns
        for col in categoricals:
            df[col] = df[col].fillna("Unknown")
            # Auto-parse temporal arrays safely
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
                    
        final_rows = len(df)
        logging.info(f"Cleaned generic data. Dropped {(initial_rows - final_rows)} empty rows.")
        
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "cleaned_dynamic_data.csv")
        df.to_csv(out_path, index=False)
        return out_path
        
    except Exception as e:
        logging.error(f"Error during dynamic cleaning: {e}")
        raise
