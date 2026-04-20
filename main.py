from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Audio Transcription API")

@app.post("/api/v1/transcribe")
async def create_transcription_job(file: UploadFile = File(...)):
    # Basic skeleton for file upload
    return {"filename": file.filename, "status": "uploaded"}
