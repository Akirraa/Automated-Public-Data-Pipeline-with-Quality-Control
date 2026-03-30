# pipeline/main.py
import time
import logging
import os
import json
from datetime import datetime

from ingest import ingest_public_sources
from clean import clean_data, update_status
from validate import run_validation
from aggregate import aggregate_metrics
from report import generate_report
from reporting import generate_pdf_report

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
    Now includes Automated Ingestion from Public Sources.
    """
    try:
        # Robust path resolution: check if we are in /pipeline or root /project
        base_dir = "."
        if not os.path.exists(os.path.join(base_dir, "data")):
            base_dir = ".."
        
        raw_dir = os.path.join(base_dir, "data", "raw")
        cleaned_dir = os.path.join(base_dir, "data", "cleaned")
        curated_dir = os.path.join(base_dir, "data", "curated")
        expectations_dir = os.path.join(base_dir, "expectations")
        log_dir = os.path.join(base_dir, "logs")
        sources_path = os.path.join(base_dir, "data", "sources.json")
        
        setup_global_logging(log_dir)
        logging.info("--- Starting Universal Auto-ETL Pipeline ---")
        update_status("Ingesting", "Scanning public data registries for updates...", 5)
        
        start_time = time.time()
        
        # 1. Ingest (Pull from external URLs if linked)
        # This will optionally overwrite 'custom_upload.csv' with the latest public data.
        ingest_public_sources(sources_path, raw_dir)
        
        # 2. Check for data presence
        raw_path = os.path.join(raw_dir, "custom_upload.csv")
        if not os.path.exists(raw_path):
            logging.error("No custom_upload.csv found in raw directory. Pipeline aborted.")
            update_status("Error", "No source CSV file detected in registries or local storage.", 0)
            return

        # 3. Clean (Refined Filtering + Imputation)
        logging.info("Phase: CLEAN (Refined)")
        cleaned_path = clean_data(raw_path, cleaned_dir)
        
        # 4. Validate (GE ephemerals)
        logging.info("Phase: VALIDATE")
        update_status("Validating", "Executing quality assurance tests...", 65)
        is_valid = run_validation(cleaned_path, expectations_dir)
        if not is_valid:
            logging.error("Validation failed. Halting pipeline.")
            update_status("Error", "Data quality validation failed.", 0)
            return
            
        # 5. Aggregate (Latest Snapshot)
        logging.info("Phase: AGGREGATE")
        update_status("Aggregating", "Performing snapshot grouping...", 80)
        agg_paths_dict = aggregate_metrics(cleaned_path, curated_dir)
        
        # 6. Report (Generation)
        logging.info("Phase: REPORT")
        update_status("Reporting", "Formatting dashboards and quality summaries...", 90)
        final_report_paths = generate_report(agg_paths_dict, curated_dir)
        
        # 7. Generate PDF Summary
        stats_path = os.path.join(cleaned_dir, "cleaning_stats.json")
        pdf_path = os.path.join(curated_dir, "quality_report.pdf")
        generate_pdf_report(stats_path, pdf_path)
        
        elapsed = time.time() - start_time
        logging.info(f"--- Pipeline Completed Automatically in {elapsed:.2f} seconds ---")
        update_status("Completed", f"Pipeline cycle successful in {elapsed:.1f}s", 100)
        
    except Exception as e:
        logging.error(f"Pipeline crashed: {e}")
        update_status("Error", f"Pipeline crash: {str(e)}", 0)

if __name__ == "__main__":
    import sys
    # Initialize status file before starting
    base = ".." if os.path.exists("../data") else "."
    if not os.path.exists(f"{base}/data"): os.makedirs(f"{base}/data", exist_ok=True)
    with open(f"{base}/data/status.json", "w") as f:
        json.dump({"phase": "Idle", "message": "Awaiting dataset...", "progress": 0}, f)
        
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        run_pipeline()
    else:
        run_pipeline()
