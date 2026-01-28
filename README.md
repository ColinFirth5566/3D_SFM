# 3D Reconstruction Web Application

A web application for creating 3D models from multiple photos using Structure from Motion (SFM) techniques.

## Features

- Upload 10-20 photos (PNG/JPG, max 1080p)
- Real-time reconstruction progress tracking
- Interactive 3D model viewer in browser
- Download 3D models as GLTF files

## Technology Stack

### Frontend
- Next.js with TypeScript
- Three.js for 3D rendering
- Tailwind CSS for styling

### Backend
- Python with FastAPI
- OpenMVG for feature extraction and matching
- OpenMVS for dense reconstruction

## Project Structure

```
3D_SFM/
├── frontend/          # Next.js application
├── backend/           # Python FastAPI server
├── docs/              # Documentation
└── CLAUDE.md          # Development guide
```

## Getting Started

See [CLAUDE.md](./CLAUDE.md) for detailed development instructions.

## Development Phases

- **Phase 0**: Core reconstruction pipeline (Current)
- **Phase 1**: Database, user authentication, and authorization
