# pipeline/main.py
import time
import logging
import os
from datetime import datetime

from clean import clean_data
from validate import run_validation
from aggregate import aggregate_metrics
from report import generate_report

def setup_global_logging(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    today_str = datetime.utcnow().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f"pipeline_log_{today_str}.txt")
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
    return log_file

def run_pipeline():
    """
    Executes the Universal Auto-ETL pipeline sequentially.
    Scraps the static Ingestion phase favoring the dynamic UI upload bridge.
    """
    try:
        base_dir = ".."
        raw_dir = os.path.join(base_dir, "data", "raw")
        cleaned_dir = os.path.join(base_dir, "data", "cleaned")
        curated_dir = os.path.join(base_dir, "data", "curated")
        expectations_dir = os.path.join(base_dir, "expectations")
        log_dir = os.path.join(base_dir, "logs")
        
        setup_global_logging(log_dir)
        logging.info("--- Starting Universal Auto-ETL Pipeline ---")
        
        start_time = time.time()
        
        # 1. Grab dynamically uploaded file explicitly, skipping 'OWID' hardcodes
        raw_path = os.path.join(raw_dir, "custom_upload.csv")
        if not os.path.exists(raw_path):
            logging.error("No custom_upload.csv found in raw directory. Pipeline aborted.")
            return

        # 2. Clean (Dynamic Data-type evaluation)
        logging.info("Phase: CLEAN (Dynamic)")
        cleaned_path = clean_data(raw_path, cleaned_dir)
        
        # 3. Validate (Dynamic Generic constraints)
        logging.info("Phase: VALIDATE (Dynamic)")
        is_valid = run_validation(cleaned_path, expectations_dir)
        if not is_valid:
            logging.error("Validation logic flagged terminal errors. Halting pipeline execution.")
            return
            
        # 4. Aggregate (Dynamic Grouping & Numerics computation)
        logging.info("Phase: AGGREGATE (Dynamic Dual-Axis)")
        agg_paths_dict = aggregate_metrics(cleaned_path, curated_dir)
        
        # 5. Report (Pass Through)
        logging.info("Phase: REPORT (Dual Mapping)")
        final_report_paths = generate_report(agg_paths_dict, curated_dir)
        
        elapsed = time.time() - start_time
        logging.info(f"--- Pipeline Completed Automatically Outputting Multi-Dimensional BI logic in {elapsed:.2f} seconds ---")
        
    except Exception as e:
        logging.error(f"Pipeline crashed due to dynamic exception triggers: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        run_pipeline()
    else:
        run_pipeline()
