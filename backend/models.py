from pydantic import BaseModel
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    job_id: str
    message: str
    file_count: int


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    stage: str
    error: Optional[str] = None
