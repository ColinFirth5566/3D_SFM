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

## OpenMVG and OpenMVS Installation

The reconstruction pipeline requires OpenMVG and OpenMVS to be installed.

### Option 1: Build from Source (Linux/Mac)

**OpenMVG**:
```bash
git clone --recursive https://github.com/openMVG/openMVG.git
cd openMVG
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=RELEASE ..
make -j4
sudo make install
```

**OpenMVS**:
```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install libboost-all-dev libopencv-dev libcgal-dev libeigen3-dev

git clone https://github.com/cdcseacave/openMVS.git
cd openMVS
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j4
sudo make install
```

### Option 2: Docker (Recommended for Development)

A Docker setup can be created to bundle OpenMVG and OpenMVS. See `docker-compose.yml`.

### Configuration

After installation, update `backend/.env`:
```
OPENMVG_BIN=/usr/local/bin/openMVG
OPENMVS_BIN=/usr/local/bin/openMVS
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
