from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
import shutil
from pathlib import Path
import asyncio

from reconstruction import ReconstructionPipeline
from models import JobStatus, UploadResponse, StatusResponse

app = FastAPI(title="3D Reconstruction API")

# CORS configuration for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory configuration
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Job tracking
jobs = {}


@app.get("/")
async def root():
    return {"message": "3D Reconstruction API", "version": "1.0.0"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_images(files: List[UploadFile] = File(...)):
    """Upload images for 3D reconstruction"""

    if len(files) < 10 or len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Please upload between 10 and 20 images"
        )

    # Validate file types
    for file in files:
        if not file.content_type in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only JPEG and PNG are allowed."
            )

    # Create job
    job_id = str(uuid.uuid4())
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    # Save uploaded files
    saved_files = []
    for idx, file in enumerate(files):
        file_extension = file.filename.split(".")[-1]
        file_path = job_dir / f"image_{idx:03d}.{file_extension}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(str(file_path))

    # Initialize job status
    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "stage": "Queued",
        "files": saved_files,
        "output_file": None,
        "error": None
    }

    # Start reconstruction in background
    asyncio.create_task(run_reconstruction(job_id))

    return UploadResponse(
        job_id=job_id,
        message=f"Successfully uploaded {len(files)} images",
        file_count=len(files)
    )


@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Get reconstruction status"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        stage=job["stage"],
        error=job.get("error")
    )


@app.get("/api/download/{job_id}")
async def download_model(job_id: str):
    """Download reconstructed 3D model"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job['status']}"
        )

    output_file = job.get("output_file")

    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Model file not found")

    return FileResponse(
        output_file,
        media_type="model/gltf+json",
        filename=f"reconstruction_{job_id}.gltf"
    )


async def run_reconstruction(job_id: str):
    """Run reconstruction pipeline in background"""

    try:
        job = jobs[job_id]
        job["status"] = "processing"
        job["stage"] = "Initializing..."

        pipeline = ReconstructionPipeline(job_id, UPLOAD_DIR, OUTPUT_DIR)

        # Run reconstruction with progress updates
        async for progress, stage in pipeline.run():
            job["progress"] = progress
            job["stage"] = stage

        # Get output file
        output_file = OUTPUT_DIR / job_id / "model.gltf"

        if output_file.exists():
            job["status"] = "completed"
            job["progress"] = 100
            job["stage"] = "Completed"
            job["output_file"] = str(output_file)
        else:
            raise Exception("Reconstruction completed but output file not found")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["stage"] = "Failed"
        print(f"Reconstruction error for job {job_id}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
