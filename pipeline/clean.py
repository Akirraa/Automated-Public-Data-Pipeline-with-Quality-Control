import pandas as pd
import numpy as np
import os
import logging
import json
from scipy.stats import median_abs_deviation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_status(phase: str, message: str, progress: int):
    """Update status file for frontend tracking."""
    status_path = os.path.join("..", "data", "status.json")
    if not os.path.exists(os.path.dirname(status_path)):
        os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w") as f:
        json.dump({"phase": phase, "message": message, "progress": progress}, f)

def enforce_monotonicity(df, loc_col, col):
    """Ensures cumulative metrics only increase over time."""
    audit_count = 0
    for loc in df[loc_col].unique():
        mask = df[loc_col] == loc
        original = df.loc[mask, col].values
        # Forward fill maximums to ensure monotonicity
        repaired = np.maximum.accumulate(np.nan_to_num(original))
        # Counts how many values actually changed
        audit_count += np.sum(repaired != original)
        df.loc[mask, col] = repaired
    return audit_count

def handle_smart_outliers(df, col, threshold=3.5):
    """Redistributes reporting spikes using Median Absolute Deviation (MAD)."""
    # Using 3.5 as recommended by Iglewicz and Hoaglin
    diff = df[col].diff().fillna(0)
    mad = median_abs_deviation(diff)
    median = np.median(diff)
    
    # Calculate Modified Z-score
    if mad == 0: return 0
    z_score = 0.6745 * (diff - median) / mad
    outlier_mask = np.abs(z_score) > threshold
    
    count = outlier_mask.sum()
    if count > 0:
        # Instead of deleting, we redistribute or smooth the spike
        # For simplicity in this audit, we'll cap to the local rolling mean
        df.loc[outlier_mask, col] = df[col].rolling(window=7, min_periods=1).mean()
    return count

def clean_data(raw_path: str, output_dir: str) -> str:
    """
    Professional Integrity Cleaning & Audit Logging:
    - Pruning: Removal of records with critical missingness.
    - Monotonicity: Repairing drops in cumulative medical metrics.
    - Outlier Redistribution: MAD-based detection of reporting anomalies.
    """
    try:
        update_status("Cleaning", "Initializing clinical integrity phase...", 10)
        df = pd.read_csv(raw_path, low_memory=False)
        initial_rows = len(df)
        audit_logs = []

        # 1. Pruning
        update_status("Cleaning", "Phase 1: Pruning invalid registrations...", 25)
        # Drop rows with critical missing IDs
        critical_cols = ['location', 'date'] if 'location' in df.columns else ['iso_code', 'date']
        df.dropna(subset=critical_cols, inplace=True)
        pruned_rows = initial_rows - len(df)
        audit_logs.append(f"Pruned {pruned_rows:,} records missing critical identifiers (location/date).")

        # 2. Data Typing
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        
        # 3. Monotonicity Enforcement (Clinical Integrity)
        update_status("Cleaning", "Phase 2: Enforcing metric monotonicity...", 50)
        mono_cols = ['total_cases', 'total_deaths', 'people_vaccinated', 'total_vaccinations']
        total_mono_repairs = 0
        loc_col = 'location' if 'location' in df.columns else 'iso_code'
        
        df.sort_values([loc_col, 'date'], inplace=True)
        for col in mono_cols:
            if col in df.columns:
                repairs = enforce_monotonicity(df, loc_col, col)
                total_mono_repairs += repairs
        
        audit_logs.append(f"Repaired {total_mono_repairs:,} monotonicity drops in cumulative caseload/mortality vectors.")

        # 4. Outlier Redistribution (MAD Optimization)
        update_status("Cleaning", "Phase 3: MAD-based outlier redistribution...", 70)
        spike_cols = ['new_cases', 'new_deaths', 'new_vaccinations']
        total_outliers = 0
        for col in spike_cols:
            if col in df.columns:
                # Fill NAs first for calculation
                df[col] = df[col].fillna(0)
                redistrib = handle_smart_outliers(df, col)
                total_outliers += redistrib
        
        audit_logs.append(f"Detected and smoothed {total_outliers:,} reporting spikes using Median Absolute Deviation.")

        # 5. Final Synthesis
        update_status("Cleaning", "Finalizing curated dataset...", 90)
        final_rows = len(df)
        
        stats = {
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "pruned_rows": pruned_rows,
            "monotonicity_verified": True,
            "monotonicity_repairs": int(total_mono_repairs),
            "outliers_redistributed": int(total_outliers),
            "features": len(df.columns),
            "audit_steps": audit_logs
        }
        
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "cleaning_stats.json"), "w") as f:
            json.dump(stats, f, indent=4)
            
        out_path = os.path.join(output_dir, "cleaned_dynamic_data.csv")
        df.to_csv(out_path, index=False)
        logging.info("Clinical cleaning completed successfully.")
        return out_path
        
    except Exception as e:
        logging.error(f"Cleaning error: {e}")
        update_status("Error", f"Clinical cleaning failed: {str(e)}", 0)
        raise
