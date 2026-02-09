# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 3D Structure from Motion (SFM) project repository.

## Project Requirements

I want to build a 3D construction website for commercial use.

The user will do the following:

1.upload 10-20 photos (png and jpg files for now, Maximum1080p resolution)
2.They will reconstruction progress animation
3.They will see the 3D model in the browser, and they can rotate it, zoom in and out, and move it around.
4.They can download the 3D model as a gltf file.

For Phase 0 development:

1.The website will be built using Next.js.
2.The 3D model will be built using Three.js.
3.The reconstruction will be built using COLMAP CLI for camera pose estimation, MVS for dense reconstruction, Poisson meshing for triangle mesh generation. Python backend handles the pipeline.
4.python returns the reconstruction result to the next.js frontend by rest api.

For phase 1 development:

1. Add database to store user information and uploaded image information and 3D model information. (I prefer to use PostgreSQL in cloudflare)
2. Add user authentication and authorization.
3. Show result here : https://yfcosmos.com/3D_SFM/

I will keep updating this file as the project progresses.

## Architecture

The project is split into two main components:

### Frontend (`/frontend`)
- **Framework**: Next.js 14 with TypeScript and App Router
- **Styling**: Tailwind CSS
- **3D Rendering**: Three.js with React Three Fiber (@react-three/fiber, @react-three/drei)
- **File Upload**: react-dropzone
- **Key Components**:
  - `app/page.tsx` - Main application page with state management
  - `components/ImageUpload.tsx` - Drag-and-drop image upload interface
  - `components/ReconstructionProgress.tsx` - Real-time progress tracking with polling
  - `components/ModelViewer.tsx` - Interactive 3D mesh viewer with vertex colors, loads GLB via useGLTF

### Backend (`/backend`)
- **Framework**: FastAPI (Python)
- **Reconstruction**: COLMAP (SfM + MVS + Poisson meshing) for vertex-colored triangle mesh, trimesh for GLB export
- **Key Files**:
  - `main.py` - FastAPI application with REST endpoints and CORS configuration
  - `models.py` - Pydantic models for request/response validation
  - `reconstruction.py` - Mesh reconstruction pipeline with COLMAP integration
- **Directories**:
  - `uploads/` - Stores uploaded images per job (auto-created)
  - `output/` - Stores reconstruction results, PLY and GLB models (auto-created)

### Data Flow
1. User uploads 10-20 images via frontend
2. Frontend sends multipart/form-data POST to `/api/upload`
3. Backend creates job ID, saves images, starts async reconstruction
4. Frontend polls `/api/status/{job_id}` every 2 seconds for progress
5. Backend runs COLMAP SfM → MVS → Poisson mesh pipeline, updating job status
6. When complete, frontend loads GLB mesh from `/api/download/{job_id}/glb`

### Reconstruction Pipeline (reconstruction.py)
The COLMAP MVS + Poisson meshing pipeline with the following stages:
1. **Image Preparation** (0-5%) - Resize and optimize input images (1000px max in fast mode)
2. **COLMAP Feature Extraction** (5-15%) - SIFT feature detection (8192 features)
3. **COLMAP Feature Matching** (15-25%) - Exhaustive matching for robust results
4. **COLMAP Mapper** (25-35%) - Structure from Motion, camera pose estimation
5. **COLMAP Undistortion** (35-40%) - Undistort images for MVS
6. **COLMAP PatchMatch MVS** (40-65%) - Dense depth map computation
7. **COLMAP Stereo Fusion** (65-75%) - Fuse depth maps into dense point cloud
8. **Poisson Meshing** (75-85%) - COLMAP poisson_mesher creates vertex-colored triangle mesh
9. **GLB Export** (85-95%) - trimesh converts mesh PLY to GLB for web viewer
10. **Finalize** (95-100%) - Verify output files

### Speed Optimizations (Fast Mode)
The pipeline includes a fast mode (default) targeting <5 minute total processing for 12 images:
- **Image Resizing**: Downscales images to 1000px max dimension
- **Full SIFT Features**: 8192 features for reliable matching
- **Exhaustive Matching**: Robust matching regardless of image capture order
- **PatchMatch MVS Speed**: window_radius=5, num_iterations=3 (vs defaults 11/5)
- **Poisson Depth**: depth=9 in fast mode (vs 11 in quality mode)

## Development Commands

### Frontend Setup
###
Please run at the funning website :
# https://yfcosmos.com/3D_SFM/
###

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure COLMAP path
python main.py  # Starts on http://localhost:8000
```

### Running Both Services
Open two terminals:
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend (with gunicorn)
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## COLMAP + Mesh Pipeline

### Installation

```bash
# Install COLMAP
sudo apt-get install colmap

# Install Python dependencies (includes trimesh for GLB export)
cd backend
pip install -r requirements.txt
```

Configure in `backend/.env`:
```
COLMAP_BIN=colmap
```

**Simulation Mode (For testing without GPU)**

No COLMAP installation required. Set in `backend/.env`:
```
GS_IMPLEMENTATION=simulation
```

### GPU Requirements

- **Minimum**: NVIDIA GPU with 4GB VRAM (for COLMAP PatchMatch MVS)
- **Recommended**: NVIDIA GPU with 8GB+ VRAM
- **CPU-only**: Use simulation mode (no actual reconstruction)

### Output Formats

- **Primary**: GLB file (vertex-colored triangle mesh) for web viewer
- **Secondary**: PLY mesh file for download/MeshLab
- Frontend uses `useGLTF` from @react-three/drei to load GLB with vertex colors

## Notes

- API uses CORS to allow frontend (localhost:3000) to access backend (localhost:8000)
- Jobs are stored in-memory; implement database for production (Phase 1)
- Uploaded files and outputs are not cleaned up automatically; add cleanup logic
- Fast mode processing: <5 minutes for 12 images with GPU (COLMAP SfM + MVS + Poisson mesh)
- Quality mode (fast_mode=False): 10-30 minutes for full resolution at 1920px
- For optimal results, ensure images have 70%+ overlap between adjacent views
- COLMAP handles everything: SfM, MVS, and Poisson meshing with vertex colors from photos
- Frontend loads GLB mesh with vertex colors; no texture mapping needed
- Download endpoint provides mesh PLY file compatible with MeshLab
