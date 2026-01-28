# API Documentation

REST API for 3D reconstruction service.

## Base URL

Development: `http://localhost:8000`

## Endpoints

### 1. Upload Images

Upload images for 3D reconstruction.

**Endpoint**: `POST /api/upload`

**Request**:
- Content-Type: `multipart/form-data`
- Body: Multiple files with key `files`

**Constraints**:
- Minimum 10 images
- Maximum 20 images
- Accepted formats: PNG, JPEG
- Recommended resolution: Up to 1080p

**Response**: `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Successfully uploaded 15 images",
  "file_count": 15
}
```

**Example** (curl):
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg" \
  # ... up to 20 files
```

### 2. Check Reconstruction Status

Get the current status of a reconstruction job.

**Endpoint**: `GET /api/status/{job_id}`

**Parameters**:
- `job_id` (path): UUID of the job

**Response**: `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "stage": "Matching features...",
  "error": null
}
```

**Status Values**:
- `queued` - Job is queued
- `processing` - Reconstruction in progress
- `completed` - Reconstruction finished
- `failed` - Reconstruction failed

**Example**:
```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000
```

### 3. Download Model

Download the reconstructed 3D model.

**Endpoint**: `GET /api/download/{job_id}`

**Parameters**:
- `job_id` (path): UUID of the job

**Response**: `200 OK`
- Content-Type: `model/gltf+json`
- Body: GLTF file

**Errors**:
- `404` - Job not found
- `400` - Job not completed

**Example**:
```bash
curl -O http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000
```

## Reconstruction Pipeline Stages

The reconstruction progresses through these stages:

1. **Analyzing images** (0-10%)
   - Image listing and validation

2. **Extracting features** (10-30%)
   - SIFT/AKAZE feature detection

3. **Matching features** (30-50%)
   - Feature matching across images

4. **Computing structure from motion** (50-70%)
   - Camera pose estimation
   - Sparse reconstruction

5. **Creating dense point cloud** (70-90%)
   - Dense reconstruction
   - Mesh generation

6. **Generating 3D model** (90-100%)
   - GLTF export

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

Error Response Format:
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider adding rate limiting to prevent abuse.

## CORS

The API allows requests from `http://localhost:3000` by default. Update `main.py` to add additional origins for production.
