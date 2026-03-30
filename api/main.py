import os
import sys
import subprocess
import json
import threading
import time
import schedule
import logging
import uuid
import numpy as np
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="Auto-ETL Dashboard API", description="Dynamic ingestion, cleaning, and reporting suite.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Source(BaseModel):
    name: str
    url: str

def trigger_pipeline():
    """Execute the pipeline subprocess safely from within the venv."""
    pipeline_dir = os.path.join("..", "pipeline")
    if os.path.exists(pipeline_dir):
        subprocess.run([sys.executable, "main.py", "--run-now"], cwd=pipeline_dir)

def run_scheduler():
    """Background thread to handle daily automated triggers."""
    schedule.every().day.at("02:00").do(trigger_pipeline)
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Universal ETL Backend Active"}

# --- SOURCES MANAGEMENT ---

@app.get("/api/sources")
def get_sources():
    path = os.path.join("..", "data", "sources.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

@app.post("/api/sources")
def add_source(source: Source):
    path = os.path.join("..", "data", "sources.json")
    sources = []
    if os.path.exists(path):
        with open(path, "r") as f:
            sources = json.load(f)
    
    new_source = {
        "id": str(uuid.uuid4()),
        "name": source.name,
        "url": source.url,
        "last_sync": "Never",
        "status": "Awaiting Sync"
    }
    sources.append(new_source)
    
    with open(path, "w") as f:
        json.dump(sources, f, indent=4)
    return new_source

@app.delete("/api/sources/{source_id}")
def delete_source(source_id: str):
    path = os.path.join("..", "data", "sources.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            sources = json.load(f)
        
        filtered = [s for s in sources if s['id'] != source_id]
        with open(path, "w") as f:
            json.dump(filtered, f, indent=4)
        return {"message": "Source removed."}
    return {"error": "Index not found."}

@app.post("/api/sources/sync")
def sync_sources(background_tasks: BackgroundTasks):
    background_tasks.add_task(trigger_pipeline)
    return {"message": "Global synchronization started."}

# --- EXISTING ENDPOINTS ---

@app.get("/api/status")
def get_pipeline_status():
    status_path = os.path.join("..", "data", "status.json")
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            return json.load(f)
    return {"phase": "Idle", "message": "Awaiting initial dataset...", "progress": 0}

@app.get("/api/logs")
def get_latest_logs():
    log_dir = os.path.join("..", "logs")
    if not os.path.exists(log_dir):
        return {"logs": "No logs found."}
    files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.startswith("pipeline_log")]
    if not files:
        return {"logs": "Pipeline has not executed logs."}
    latest_file = max(files, key=os.path.getmtime)
    with open(latest_file, "r") as f:
        lines = f.readlines()
        return {"logs": "".join(lines[-100:])}

@app.post("/api/upload")
async def upload_dataset(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    raw_dir = os.path.join("..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    file_location = os.path.join(raw_dir, "custom_upload.csv")
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    status_path = os.path.join("..", "data", "status.json")
    with open(status_path, "w") as f:
        json.dump({"phase": "Starting", "message": "File received. Analysis starting...", "progress": 5}, f)
        
    background_tasks.add_task(trigger_pipeline)
    return {"status": "Upload successful"}

@app.get("/api/download/csv")
def download_cleaned_csv():
    path = os.path.join("..", "data", "cleaned", "cleaned_dynamic_data.csv")
    if os.path.exists(path):
        return FileResponse(path, filename="cleaned_dataset.csv", media_type="text/csv")
    return JSONResponse(status_code=404, content={"message": "Cleaned file not found."})

@app.get("/api/pbi")
def power_bi_connector():
    path = os.path.join("..", "data", "cleaned", "cleaned_dynamic_data.csv")
    if os.path.exists(path):
        return FileResponse(path, media_type="application/octet-stream")
    return JSONResponse(status_code=404, content={"message": "Data not yet available for sync."})

@app.get("/api/download/pdf")
def download_pdf_report():
    path = os.path.join("..", "data", "curated", "quality_report.pdf")
    if os.path.exists(path):
        return FileResponse(path, filename="data_quality_report.pdf", media_type="application/pdf")
    return JSONResponse(status_code=404, content={"message": "PDF report not available."})

@app.get("/api/metrics")
def get_metrics():
    curated_dir = os.path.join("..", "data", "curated")
    entity_path = os.path.join(curated_dir, "report_entity.csv")
    time_path = os.path.join(curated_dir, "report_time.csv")
    if not os.path.exists(entity_path):
        return {"error": "Dashboard data unavailable."}
    try:
        df_entity = pd.read_csv(entity_path)
        entity_data = df_entity.fillna(np.nan).replace([np.nan], [None]).to_dict(orient="records")
        time_data = []
        if os.path.exists(time_path):
            df_time = pd.read_csv(time_path)
            time_data = df_time.fillna(np.nan).replace([np.nan], [None]).to_dict(orient="records")
        return {"entity": entity_data, "time": time_data}
    except Exception as e:
        return {"error": f"Parsing failed: {str(e)}"}
