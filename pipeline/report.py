import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_report(aggregated_paths: dict, output_dir: str) -> dict:
    """
    Passthrough dynamic schemas explicitly isolating the Temporal paths from Entity paths dict.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        out_paths = {}
        
        if 'entity' in aggregated_paths:
            p = os.path.join(output_dir, "report_entity.csv")
            shutil.copy(aggregated_paths['entity'], p)
            out_paths['entity'] = p
            
        if 'time' in aggregated_paths:
            p = os.path.join(output_dir, "report_time.csv")
            shutil.copy(aggregated_paths['time'], p)
            out_paths['time'] = p
            
        logging.info(f"Dynamic final reports synced effectively in Custom Maps.")
        return out_paths
    except Exception as e:
        logging.error(f"Error generating dynamic report copy: {e}")
        raise
