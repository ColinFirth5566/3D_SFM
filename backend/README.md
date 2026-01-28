# Backend API

Python FastAPI backend for 3D reconstruction using 3D Gaussian Splatting (3DGS).

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your COLMAP and 3DGS paths
```

## Running the Server

Development mode:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

- `POST /api/upload` - Upload images for reconstruction
- `GET /api/status/{job_id}` - Check reconstruction status
- `GET /api/download/{job_id}` - Download completed 3D model

## 3D Gaussian Splatting Setup

This backend supports multiple 3DGS implementations:

### Option 1: Original 3DGS (Recommended for best quality)

**Prerequisites:**
- CUDA-capable GPU (NVIDIA)
- CUDA Toolkit 11.6+
- Python 3.7+

**Installation:**

1. Install COLMAP:
```bash
# Ubuntu/Debian
sudo apt-get install colmap

# Or build from source: https://colmap.github.io/install.html
```

2. Clone and install 3D Gaussian Splatting:
```bash
cd /opt
git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive
cd gaussian-splatting

# Install submodules
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

# Install additional dependencies
pip install plyfile tqdm
```

3. Update `.env`:
```bash
COLMAP_BIN=/usr/bin/colmap
GS_IMPLEMENTATION=original
GAUSSIAN_SPLATTING_PATH=/opt/gaussian-splatting
```

### Option 2: Nerfstudio with Splatfacto

**Installation:**
```bash
pip install nerfstudio

# Process data and train
ns-install-cli
```

**Update `.env`:**
```bash
COLMAP_BIN=colmap
GS_IMPLEMENTATION=nerfstudio
```

### Option 3: Simulation Mode (For testing without GPU)

No additional setup required. The pipeline will simulate the reconstruction process.

**Update `.env`:**
```bash
GS_IMPLEMENTATION=simulation
```

## Pipeline Stages

The 3DGS reconstruction pipeline consists of:

1. **Image Preparation** (0-5%) - Copy and organize input images
2. **COLMAP Feature Extraction** (5-20%) - Detect SIFT features in images
3. **COLMAP Feature Matching** (20-35%) - Match features across images
4. **COLMAP Mapper** (35-50%) - Structure from Motion, camera pose estimation
5. **COLMAP Undistortion** (50-55%) - Undistort images for training
6. **3DGS Training** (55-95%) - Train gaussian splat representation
7. **Model Export** (95-100%) - Export to PLY/GLTF format

## Outputs

The reconstruction produces:
- `model.ply` - 3D Gaussian Splat point cloud
- `model.gltf` - GLTF reference file
- COLMAP sparse reconstruction data
- Training logs and checkpoints

## GPU Requirements

- **Minimum**: NVIDIA GPU with 8GB VRAM (GTX 1070 or better)
- **Recommended**: NVIDIA GPU with 12GB+ VRAM (RTX 3080 or better)
- **CPU-only**: Use simulation mode for testing (no actual reconstruction)

## Troubleshooting

**COLMAP not found:**
- Ensure COLMAP is installed and in PATH
- Set `COLMAP_BIN` in `.env` to the full path

**CUDA out of memory:**
- Reduce image resolution before upload
- Use fewer images (10-15 instead of 20)
- Reduce training iterations in `reconstruction.py`

**3DGS training fails:**
- Check GPU availability: `nvidia-smi`
- Verify CUDA installation: `nvcc --version`
- Check 3DGS installation path in `.env`

**No output model:**
- Check `backend/output/{job_id}/` for error logs
- Verify COLMAP successfully created sparse reconstruction
- Ensure sufficient disk space

## Performance Tips

- Use images with good overlap (70%+ between adjacent images)
- Maintain consistent lighting across images
- Avoid motion blur
- Use 1080p or lower resolution for faster processing
- Expect 10-30 minutes for full reconstruction with GPU
