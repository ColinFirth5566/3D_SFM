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
3.The reconstruction will be built using OpenMVG and OpenMVS, I want a python backend, and python calls c++ to do reconstruction and get the result.
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
- **Key Files**:
  - `main.py` - FastAPI application with REST endpoints and CORS configuration
  - `models.py` - Pydantic models for request/response validation
  - `reconstruction.py` - OpenMVG/OpenMVS integration pipeline
- **Directories**:
  - `uploads/` - Stores uploaded images per job (auto-created)
  - `output/` - Stores reconstruction results and GLTF models (auto-created)

### Data Flow
1. User uploads 10-20 images via frontend
2. Frontend sends multipart/form-data POST to `/api/upload`
3. Backend creates job ID, saves images, starts async reconstruction
4. Frontend polls `/api/status/{job_id}` every 2 seconds for progress
5. Backend runs OpenMVG → OpenMVS pipeline, updating job status
6. When complete, frontend displays 3D model from `/api/download/{job_id}`

### Reconstruction Pipeline (reconstruction.py)
The pipeline simulates the following stages (needs actual OpenMVG/OpenMVS integration):
1. **Image Analysis** (0-10%) - Create SFM data structure
2. **Feature Extraction** (10-30%) - SIFT/AKAZE feature detection
3. **Feature Matching** (30-50%) - Match features across images
4. **Structure from Motion** (50-70%) - Incremental SFM, camera pose estimation
5. **Dense Reconstruction** (70-90%) - OpenMVS dense point cloud and meshing
6. **GLTF Export** (90-100%) - Convert mesh to GLTF format

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
cp .env.example .env  # Configure OpenMVG/OpenMVS paths
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

## OpenMVG/OpenMVS Integration

**IMPORTANT**: The current implementation uses placeholder/simulation for the reconstruction pipeline. To enable actual 3D reconstruction:

1. **Install OpenMVG**:
   - Clone from https://github.com/openMVG/openMVG
   - Build and install following their documentation
   - Note the installation path of binaries

2. **Install OpenMVS**:
   - Clone from https://github.com/cdcseacave/openMVS
   - Install dependencies (Eigen, Boost, OpenCV, CGAL)
   - Build and install
   - Note the installation path of binaries

3. **Configure Backend**:
   - Update `backend/.env` with correct paths:
     ```
     OPENMVG_BIN=/path/to/openmvg/bin
     OPENMVS_BIN=/path/to/openmvs/bin
     ```

4. **Implement Real Pipeline**:
   - Update `reconstruction.py` methods to call actual binaries via subprocess
   - Add mesh to GLTF conversion (consider using `obj2gltf` or `assimp`)

## Notes

- API uses CORS to allow frontend (localhost:3000) to access backend (localhost:8000)
- Jobs are stored in-memory; implement database for production (Phase 1)
- Uploaded files and outputs are not cleaned up automatically; add cleanup logic
- GLTF export currently generates placeholder; needs mesh converter integration
