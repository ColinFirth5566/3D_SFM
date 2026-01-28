# 3D Gaussian Splatting Setup Guide

Complete guide for setting up 3D Gaussian Splatting reconstruction.

## Overview

This project uses:
- **COLMAP**: Structure from Motion (camera pose estimation)
- **3D Gaussian Splatting (3DGS)**: Neural scene reconstruction
- **Backend**: Python FastAPI with async pipeline
- **Frontend**: Next.js with Three.js for visualization

## Hardware Requirements

### Minimum
- CPU: Modern multi-core processor (Intel i5/AMD Ryzen 5 or better)
- RAM: 16GB
- GPU: NVIDIA GPU with 8GB VRAM (GTX 1070, RTX 2060, or better)
- Storage: 50GB free space

### Recommended
- CPU: High-performance multi-core (Intel i7/AMD Ryzen 7 or better)
- RAM: 32GB+
- GPU: NVIDIA GPU with 12GB+ VRAM (RTX 3080, RTX 4070, or better)
- Storage: 100GB+ SSD

### CPU-Only Mode
- For testing without GPU, use `GS_IMPLEMENTATION=simulation` mode
- No actual reconstruction, but tests the full pipeline

## Software Prerequisites

### 1. CUDA Toolkit (For GPU acceleration)

**Check if CUDA is installed:**
```bash
nvcc --version
nvidia-smi
```

**Install CUDA 11.8** (recommended):
```bash
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

Add to `~/.bashrc`:
```bash
export PATH=/usr/local/cuda-11.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH
```

### 2. Python 3.9+

```bash
python --version  # Should be 3.9 or higher
```

### 3. PyTorch with CUDA

```bash
# Install PyTorch with CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify installation
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA version: {torch.version.cuda}')"
```

## Installation Steps

### Step 1: Install COLMAP

COLMAP is required for Structure from Motion (camera pose estimation).

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install \
    git \
    cmake \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgtest-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev

# Install COLMAP
sudo apt-get install colmap
```

**macOS:**
```bash
brew install colmap
```

**Verify installation:**
```bash
colmap -h
```

### Step 2: Install 3D Gaussian Splatting

Choose one of the following implementations:

#### Option A: Original 3DGS (Recommended)

Best quality, requires GPU.

```bash
# Navigate to installation directory
cd /opt
sudo mkdir -p gaussian-splatting
sudo chown $USER:$USER gaussian-splatting

# Clone repository
git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive gaussian-splatting
cd gaussian-splatting

# Install submodules (C++/CUDA extensions)
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

# Install Python dependencies
pip install plyfile tqdm
```

**Configure backend:**

Edit `backend/.env`:
```bash
COLMAP_BIN=colmap
GS_IMPLEMENTATION=original
GAUSSIAN_SPLATTING_PATH=/opt/gaussian-splatting
```

#### Option B: Nerfstudio (Easier, cross-platform)

Good quality, easier installation.

```bash
# Install nerfstudio
pip install nerfstudio

# Install CLI tools
ns-install-cli

# Verify installation
ns-train --help
```

**Configure backend:**

Edit `backend/.env`:
```bash
COLMAP_BIN=colmap
GS_IMPLEMENTATION=nerfstudio
```

#### Option C: Simulation Mode (No GPU)

For testing the pipeline without GPU or 3DGS installation.

**Configure backend:**

Edit `backend/.env`:
```bash
GS_IMPLEMENTATION=simulation
```

### Step 3: Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cd backend
cp .env.example .env
nano .env  # Edit configuration
```

**Example `.env` configurations:**

**For Original 3DGS:**
```env
COLMAP_BIN=colmap
GS_IMPLEMENTATION=original
GAUSSIAN_SPLATTING_PATH=/opt/gaussian-splatting
HOST=0.0.0.0
PORT=8000
```

**For Nerfstudio:**
```env
COLMAP_BIN=colmap
GS_IMPLEMENTATION=nerfstudio
HOST=0.0.0.0
PORT=8000
```

**For Simulation:**
```env
GS_IMPLEMENTATION=simulation
HOST=0.0.0.0
PORT=8000
```

## Testing the Installation

### 1. Test Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit http://localhost:8000/docs to see the API documentation.

### 2. Test Frontend

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 to see the application.

### 3. Test Full Pipeline

1. Prepare 10-20 test images (overlapping views of an object/scene)
2. Upload through the web interface
3. Monitor reconstruction progress
4. View the resulting 3D model

## Performance Tuning

### For Faster Reconstruction

Edit `backend/reconstruction.py` line ~200:
```python
"--iterations", "3000",  # Reduce from 7000 for faster training
```

### For Better Quality

```python
"--iterations", "30000",  # Increase for better quality
```

### Memory Optimization

If you encounter CUDA out of memory errors:

1. Reduce image resolution (use 720p instead of 1080p)
2. Use fewer images (10-12 instead of 20)
3. Reduce training iterations

## Troubleshooting

### COLMAP Issues

**Error: "colmap: command not found"**
- Install COLMAP: `sudo apt-get install colmap`
- Or set full path in `.env`: `COLMAP_BIN=/usr/local/bin/colmap`

**COLMAP fails with "No CUDA-enabled device"**
- COLMAP will fallback to CPU automatically
- Edit `reconstruction.py` to disable GPU features:
  ```python
  "--SiftExtraction.use_gpu", "0",
  ```

### 3DGS Issues

**Error: "No module named 'diff_gaussian_rasterization'"**
- Reinstall submodules:
  ```bash
  cd /opt/gaussian-splatting
  pip install submodules/diff-gaussian-rasterization --force-reinstall
  ```

**CUDA Out of Memory**
- Reduce image resolution
- Use fewer images
- Reduce training iterations
- Use a GPU with more VRAM

**Training produces poor results**
- Ensure images have good overlap (70%+)
- Use consistent lighting
- Avoid motion blur
- Capture from multiple angles

### General Issues

**Backend crashes during reconstruction**
- Check logs in backend console
- Verify COLMAP installation
- Ensure sufficient disk space
- Check GPU memory usage: `nvidia-smi`

**Frontend can't connect to backend**
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Ensure firewall allows connections

## Next Steps

After successful installation:

1. Test with sample images
2. Optimize training parameters for your use case
3. Consider implementing file cleanup
4. Add logging for debugging
5. Explore frontend updates for better gaussian splat visualization

## Advanced: Docker Installation

For a containerized setup (work in progress):

```bash
docker-compose up
```

See `docker-compose.yml` for configuration.

## Resources

- Original 3DGS Paper: https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
- 3DGS GitHub: https://github.com/graphdeco-inria/gaussian-splatting
- COLMAP Documentation: https://colmap.github.io/
- Nerfstudio: https://docs.nerf.studio/

## Support

For issues:
1. Check this guide first
2. Review error logs in backend console
3. Verify all prerequisites are installed
4. Test with simulation mode to isolate issues
5. Open an issue on GitHub with error details
