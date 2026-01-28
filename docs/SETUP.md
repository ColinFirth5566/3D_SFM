# Setup Guide

This guide will help you set up the 3D Reconstruction Web Application.

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git

## Quick Start (Development)

1. **Clone and navigate to the repository**
   ```bash
   cd 3D_SFM
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Run both services**

   Open two terminal windows:

   **Terminal 1 (Backend)**:
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   python main.py
   ```

   **Terminal 2 (Frontend)**:
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

## 3D Gaussian Splatting and COLMAP Installation

The reconstruction pipeline uses COLMAP for camera pose estimation and 3D Gaussian Splatting for reconstruction.

### Prerequisites

- **GPU**: NVIDIA GPU with 8GB+ VRAM (for production)
- **CUDA**: Version 11.6 or higher
- **Python**: 3.7+

### Step 1: Install COLMAP

**Ubuntu/Debian**:
```bash
sudo apt-get install colmap
```

**macOS** (Homebrew):
```bash
brew install colmap
```

**From Source**:
```bash
git clone https://github.com/colmap/colmap.git
cd colmap
mkdir build && cd build
cmake .. -GNinja
ninja
sudo ninja install
```

Verify installation:
```bash
colmap -h
```

### Step 2: Install 3D Gaussian Splatting

**Option A: Original 3DGS (Recommended for production)**

1. Install CUDA and PyTorch:
```bash
# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

2. Clone and install 3DGS:
```bash
cd /opt
sudo git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive
cd gaussian-splatting

# Install submodules
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

# Install other dependencies
pip install plyfile tqdm
```

3. Update `backend/.env`:
```bash
COLMAP_BIN=colmap
GS_IMPLEMENTATION=original
GAUSSIAN_SPLATTING_PATH=/opt/gaussian-splatting
```

**Option B: Nerfstudio with Splatfacto (Easier setup)**

```bash
pip install nerfstudio
ns-install-cli
```

Update `backend/.env`:
```bash
COLMAP_BIN=colmap
GS_IMPLEMENTATION=nerfstudio
```

**Option C: Simulation Mode (No GPU required)**

For testing without GPU or 3DGS installation:

Update `backend/.env`:
```bash
GS_IMPLEMENTATION=simulation
```

### Verify Installation

Check CUDA:
```bash
nvcc --version
nvidia-smi
```

Check PyTorch CUDA:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Testing the Setup

1. Start both frontend and backend
2. Navigate to http://localhost:3000
3. Try uploading 10-20 test images
4. Watch the reconstruction progress
5. View and download the resulting 3D model

## Troubleshooting

**Port already in use**:
- Change the port in `backend/main.py` or `frontend/package.json`

**CORS errors**:
- Ensure backend CORS settings in `main.py` include your frontend URL

**Module not found**:
- Ensure virtual environment is activated for Python
- Run `npm install` again for frontend

**OpenMVG/OpenMVS not found**:
- Verify installation paths
- Update paths in `backend/.env`
- Ensure binaries are executable

## Next Steps

- See `CLAUDE.md` for architecture details
- See `README.md` for project overview
- Check API documentation at http://localhost:8000/docs
