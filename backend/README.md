# Backend API

Python FastAPI backend for 3D reconstruction.

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
# Edit .env with your OpenMVG/OpenMVS paths
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

## OpenMVG/OpenMVS Integration

This backend requires OpenMVG and OpenMVS to be installed on the system.

### Installation (Ubuntu/Debian)

Install dependencies and build from source. See:
- OpenMVG: https://github.com/openMVG/openMVG
- OpenMVS: https://github.com/cdcseacave/openMVS

Update the `.env` file with the correct binary paths after installation.
