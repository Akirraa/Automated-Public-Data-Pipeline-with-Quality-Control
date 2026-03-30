import os
import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_status(phase: str, message: str, progress: int):
    """Refined status tracking for the ingestion phase."""
    status_path = os.path.join("..", "data", "status.json")
    if not os.path.exists(os.path.dirname(status_path)):
        os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w") as f:
        json.dump({"phase": phase, "message": message, "progress": progress}, f)

def ingest_public_sources(sources_path: str, output_dir: str):
    """
    Iterates through linked public sources, downloads CSVs, and prepares raw storage.
    """
    if not os.path.exists(sources_path):
        logging.warning("No sources.json found. Skipping public ingestion.")
        return []

    try:
        with open(sources_path, "r") as f:
            sources = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read sources file: {e}")
        return []

    downloaded_files = []
    os.makedirs(output_dir, exist_ok=True)

    for i, source in enumerate(sources):
        try:
            name = source.get('name', 'Unknown Source')
            url = source.get('url')
            if not url: continue

            update_status("Ingesting", f"Fetching fresh data from {name}...", int((i / len(sources)) * 100))
            logging.info(f"Downloading from {name}: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save with a standardized name for the pipeline to find
            # For now, we save individual files but 'custom_upload.csv' remains the primary 
            # if the user manually uploaded. If they synced, we overwrite 'custom_upload.csv' 
            # with the main source or leave it in raw/ for the cleaner to pick highest quality.
            
            # To simplify for the Universal Dashboard: the LAST successful sync becomes 'custom_upload.csv'
            file_path = os.path.join(output_dir, "custom_upload.csv")
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            # Update source metadata
            source['last_sync'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            source['status'] = "Success"
            downloaded_files.append(file_path)
            
        except Exception as e:
            logging.error(f"Failed to ingest {source.get('name')}: {e}")
            source['status'] = f"Failed: {str(e)}"

    # Save updated sources metadata back to disk
    with open(sources_path, "w") as f:
        json.dump(sources, f, indent=4)

    return downloaded_files

if __name__ == "__main__":
    # Context-aware pathing for CLI execution
    base = ".." if os.path.exists("../data") else "."
    ingest_public_sources(os.path.join(base, "data", "sources.json"), os.path.join(base, "data", "raw"))
