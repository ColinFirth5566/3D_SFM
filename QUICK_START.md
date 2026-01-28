# Quick Start Guide - Get Running in 5 Minutes

## The Problem
You visited https://colinfirth5566.github.io/3D_SFM/ and uploaded images, but got an error.

**Why?** The frontend is on GitHub Pages, but the backend (which does the 3D reconstruction) needs to run on your computer.

## The Solution - Start the Backend

### Step 1: Open Terminal/Command Prompt

Navigate to your project directory:
```bash
cd /mnt/c/Code/3D_SFM
```

### Step 2: Set Up Backend (First Time Only)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this takes 2-3 minutes)
pip install -r requirements.txt

# Configure for testing mode
cp .env.example .env
echo "GS_IMPLEMENTATION=simulation" >> .env
```

### Step 3: Run the Backend

```bash
# Make sure you're in backend directory and venv is activated
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Backend is now running!**

### Step 4: Use the App

1. Keep the terminal window open (backend must stay running)
2. Go back to: https://colinfirth5566.github.io/3D_SFM/
3. Upload your images again
4. Watch the progress!

## Next Time

After the first setup, you just need:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

## What Happens Now?

With `GS_IMPLEMENTATION=simulation` mode:
- Backend receives your images ✅
- Simulates the reconstruction process ✅
- Shows progress animation ✅
- Creates a placeholder model ✅

**For REAL 3D reconstruction**, you need to:
1. Install COLMAP
2. Install 3D Gaussian Splatting
3. Have an NVIDIA GPU
4. See: `docs/3DGS_SETUP.md`

## Troubleshooting

**"python: command not found"**
- Try `python3` instead of `python`
- Install Python from python.org

**"venv/bin/activate: No such file"**
- Make sure you created the venv first: `python -m venv venv`
- You should be in the `backend` directory

**"Port 8000 already in use"**
- Another process is using port 8000
- Kill it: `lsof -ti:8000 | xargs kill -9` (Mac/Linux)
- Or change port in `main.py` to 8001

**Still getting errors on GitHub Pages?**
- Make sure backend shows "Uvicorn running on http://0.0.0.0:8000"
- Refresh the GitHub Pages browser tab
- Check browser console (F12) for new errors

## Architecture

```
┌─────────────────────────────────┐
│   GitHub Pages (Your Browser)  │
│  colinfirth5566.github.io/...   │  ← You see this
│                                 │
│  Frontend: Upload UI, Viewer    │
└────────────┬────────────────────┘
             │
             │ HTTP Requests
             ▼
┌─────────────────────────────────┐
│   Your Computer                 │
│   localhost:8000                │  ← You run this
│                                 │
│  Backend: Python + FastAPI      │
│  3DGS reconstruction            │
└─────────────────────────────────┘
```

## Ready?

```bash
cd /mnt/c/Code/3D_SFM/backend
source venv/bin/activate
python main.py
```

Then visit: https://colinfirth5566.github.io/3D_SFM/
