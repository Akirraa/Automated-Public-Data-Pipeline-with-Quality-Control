import os
import sys
import subprocess
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(title="Auto-ETL Data API", description="Accepts generic CSVs and serves curated dynamic metrics.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def trigger_pipeline():
    pipeline_dir = os.path.join("..", "pipeline")
    if os.path.exists(pipeline_dir):
        subprocess.run([sys.executable, "main.py", "--run-now"], cwd=pipeline_dir)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Universal ETL Backend is running."}

@app.post("/api/upload")
async def upload_dataset(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    raw_dir = os.path.join("..", "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    file_location = os.path.join(raw_dir, "custom_upload.csv")
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    background_tasks.add_task(trigger_pipeline)
    return {"info": f"File '{file.filename}' securely vaulted. Analysis starting...", "status": "Pipeline Processing Scheduled"}

@app.get("/api/metrics")
def get_metrics():
    """
    Returns Dual-Axis BI metrics: Entities grouped vs Temporal arrays seamlessly.
    """
    curated_dir = os.path.join("..", "data", "curated")
    if not os.path.exists(curated_dir):
         curated_dir = os.path.join("data", "curated")
         
    entity_path = os.path.join(curated_dir, "report_entity.csv")
    time_path = os.path.join(curated_dir, "report_time.csv")
    
    if not os.path.exists(entity_path):
        return {"error": "Pipeline data not found. Please upload a CSV."}
        
    try:
        df_entity = pd.read_csv(entity_path)
        df_entity = df_entity.where(pd.notnull(df_entity), None)
        
        time_data = []
        if os.path.exists(time_path):
            df_time = pd.read_csv(time_path)
            df_time = df_time.where(pd.notnull(df_time), None)
            time_data = df_time.to_dict(orient="records")
            
        return {
            "entity": df_entity.to_dict(orient="records"),
            "time": time_data
        }
    except Exception as e:
        return {"error": f"Failed to parse dynamically generated report correctly: {str(e)}"}
