import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException

from transcriber import transcriber

app = FastAPI(title="Audio Transcription API")

# Simple in-memory store for prototype
# TODO: Replace with Redis + Postgres for persistent job tracking across instances
jobs: dict[str, dict] = {}

def process_audio_task(job_id: str, file_path: Path):
    try:
        jobs[job_id]["status"] = "processing"
        result = transcriber.process_file(file_path)
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
    finally:
        # Prevent disk space leaks by explicitly cleaning up
        if file_path.exists():
            file_path.unlink()

@app.post("/api/v1/transcribe")
async def create_transcription_job(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    job_id = str(uuid.uuid4())
    suffix = Path(file.filename).suffix
    
    # We maintain the original file extension so ffmpeg can correctly infer the container
    temp_file = Path(f"/tmp/{job_id}{suffix}")
    
    try:
        # Streaming directly to disk to avoid blowing up memory on large files
        with open(temp_file, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to persist uploaded file")
        
    jobs[job_id] = {"status": "queued"}
    
    # BackgroundTasks executes in the default ThreadPoolExecutor.
    # TODO: In a real production environment, replace this with Celery + Redis for durability and distributed workers.
    background_tasks.add_task(process_audio_task, job_id, temp_file)
    
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return jobs[job_id]
