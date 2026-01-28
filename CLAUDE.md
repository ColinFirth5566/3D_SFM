# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 3D Structure from Motion (SFM) project repository. The codebase is currently empty or in its initial state.

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
3.The reconstruction will be built using 3D Gaussian Splatting (3DGS), with COLMAP for camera pose estimation. Python backend handles the pipeline.
4.python returns the reconstruction result to the next.js frontend by rest api.

For phase 1 development:

1. Add database to store user information and uploaded image information and 3D model information.
2. Add user authentication and authorization.

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
  - `components/ModelViewer.tsx` - Interactive 3D model viewer with OrbitControls

### Backend (`/backend`)
- **Framework**: FastAPI (Python)
- **Reconstruction**: 3D Gaussian Splatting with COLMAP
- **Key Files**:
  - `main.py` - FastAPI application with REST endpoints and CORS configuration
  - `models.py` - Pydantic models for request/response validation
  - `reconstruction.py` - 3DGS pipeline with COLMAP integration
- **Directories**:
  - `uploads/` - Stores uploaded images per job (auto-created)
  - `output/` - Stores reconstruction results, PLY and GLTF models (auto-created)

### Data Flow
1. User uploads 10-20 images via frontend
2. Frontend sends multipart/form-data POST to `/api/upload`
3. Backend creates job ID, saves images, starts async reconstruction
4. Frontend polls `/api/status/{job_id}` every 2 seconds for progress
5. Backend runs COLMAP → 3DGS training pipeline, updating job status
6. When complete, frontend displays 3D model from `/api/download/{job_id}`

### Reconstruction Pipeline (reconstruction.py)
The 3D Gaussian Splatting pipeline with the following stages:
1. **Image Preparation** (0-5%) - Copy and organize input images
2. **COLMAP Feature Extraction** (5-20%) - SIFT feature detection
3. **COLMAP Feature Matching** (20-35%) - Match features across images
4. **COLMAP Mapper** (35-50%) - Structure from Motion, camera pose estimation
5. **COLMAP Undistortion** (50-55%) - Undistort images for training
6. **3DGS Training** (55-95%) - Train gaussian splat representation
7. **Model Export** (95-100%) - Export to PLY/GLTF format

## Development Commands

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure COLMAP and 3DGS paths
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

## 3D Gaussian Splatting Integration

The backend supports multiple 3DGS implementations with automatic detection.

### Installation Options

**Option 1: Original 3DGS (Recommended for production)**

Requirements: NVIDIA GPU with CUDA 11.6+

```bash
# Install COLMAP
sudo apt-get install colmap

# Clone and install 3DGS
cd /opt
git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive
cd gaussian-splatting
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn
```

Configure in `backend/.env`:
```
COLMAP_BIN=colmap
GS_IMPLEMENTATION=original
GAUSSIAN_SPLATTING_PATH=/opt/gaussian-splatting
```

**Option 2: Nerfstudio with Splatfacto**

```bash
pip install nerfstudio
ns-install-cli
```

Configure in `backend/.env`:
```
GS_IMPLEMENTATION=nerfstudio
```

**Option 3: Simulation Mode (For testing without GPU)**

No installation required. Set in `backend/.env`:
```
GS_IMPLEMENTATION=simulation
```

### GPU Requirements

- **Minimum**: NVIDIA GPU with 8GB VRAM (GTX 1070+)
- **Recommended**: NVIDIA GPU with 12GB+ VRAM (RTX 3080+)
- **CPU-only**: Use simulation mode (no actual reconstruction)

### Output Formats

- **Primary**: PLY file with 3D gaussian splats
- **Secondary**: GLTF reference file
- Frontend should use a gaussian splat viewer for best results

## Notes

- API uses CORS to allow frontend (localhost:3000) to access backend (localhost:8000)
- Jobs are stored in-memory; implement database for production (Phase 1)
- Uploaded files and outputs are not cleaned up automatically; add cleanup logic
- 3DGS training requires 10-30 minutes with GPU (depending on image count and resolution)
- For optimal results, ensure images have 70%+ overlap between adjacent views
- COLMAP handles camera pose estimation; 3DGS handles the reconstruction
