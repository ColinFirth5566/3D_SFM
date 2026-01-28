# GitHub Pages Deployment Guide

This guide explains how to view the 3D Reconstruction frontend on GitHub Pages.

## Important Notes

⚠️ **GitHub Pages hosts the FRONTEND only**. The backend API must be run separately.

The frontend will be available at: `https://colinfirth5566.github.io/3D_SFM/`

## What GitHub Pages Provides

- **Static frontend hosting** - The Next.js app built as static HTML/CSS/JS
- **Public access** - Anyone can view the interface
- **Free hosting** - No cost for public repositories

## What GitHub Pages Does NOT Provide

- **Backend API** - You must run the Python backend separately
- **3D Reconstruction** - The actual reconstruction happens on your backend
- **File storage** - Uploads/outputs are handled by your backend

## Setup Steps

### 1. Enable GitHub Pages

I'll enable this for you automatically, but here's how it works:

1. Go to repository Settings
2. Navigate to "Pages" section
3. Source: "GitHub Actions"
4. The workflow will deploy automatically on push to master

### 2. Deployment Process

Every time you push to `master` branch:

1. GitHub Actions runs the workflow (`.github/workflows/deploy.yml`)
2. Builds the Next.js app as static files
3. Deploys to GitHub Pages
4. Available at `https://colinfirth5566.github.io/3D_SFM/`

### 3. Using the Deployed Frontend

Since the backend is not on GitHub Pages:

**Option A: Run Backend Locally**

1. Clone the repository
2. Run the backend locally:
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```
3. Visit `https://colinfirth5566.github.io/3D_SFM/`
4. The frontend will connect to `http://localhost:8000`

**Option B: Deploy Backend Elsewhere**

Deploy the backend to a cloud service:
- **Heroku**: Python app hosting
- **Railway**: Easy Python deployment
- **AWS EC2**: Full control, GPU support
- **Google Cloud Run**: Containerized deployment
- **DigitalOcean**: VPS with GPU options

Then update the frontend API URL:
```bash
# In .github/workflows/deploy.yml, line 40:
NEXT_PUBLIC_API_URL: https://your-backend-url.com
```

## Architecture with GitHub Pages

```
┌─────────────────────────────────────┐
│   GitHub Pages (Frontend Only)     │
│  https://username.github.io/3D_SFM  │
│                                     │
│  - Upload UI                        │
│  - Progress Display                 │
│  - 3D Viewer                        │
└──────────────┬──────────────────────┘
               │
               │ API Calls (CORS)
               │
               ▼
┌─────────────────────────────────────┐
│   Backend (Run Separately)          │
│   - Local: http://localhost:8000    │
│   - Cloud: https://your-api.com     │
│                                     │
│  - FastAPI Server                   │
│  - COLMAP Processing                │
│  - 3DGS Training                    │
│  - File Storage                     │
└─────────────────────────────────────┘
```

## CORS Configuration

The backend must allow requests from GitHub Pages:

Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://colinfirth5566.github.io"  # Add this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

**Frontend loads but can't connect to backend:**
- Ensure backend is running
- Check CORS settings in backend
- Verify API URL in frontend config
- Check browser console for errors

**404 errors on GitHub Pages:**
- Wait 5-10 minutes after first deployment
- Check Actions tab for deployment status
- Ensure workflow completed successfully

**API calls failing:**
- Backend must be accessible from browser
- HTTPS frontend can't call HTTP backend (mixed content)
- Consider using ngrok or similar for local backend

## Local Testing of Static Build

Test the static build locally before deploying:

```bash
cd frontend
npm run build
npx serve out
```

Visit `http://localhost:3000` to test the static site.

## Manual Deployment

If automatic deployment doesn't work:

```bash
cd frontend
npm run build
# Copy the 'out' directory contents to GitHub Pages branch
```

## Monitoring Deployments

View deployment status:
1. Go to repository on GitHub
2. Click "Actions" tab
3. See "Deploy to GitHub Pages" workflows
4. Click on a run to see details

## Recommended Setup for Demo

For a complete working demo:

1. **Backend**: Deploy to Railway or Heroku (free tier)
2. **Frontend**: Auto-deployed to GitHub Pages
3. Update `NEXT_PUBLIC_API_URL` in workflow to backend URL
4. Share the GitHub Pages URL for demos

## Next Steps

After GitHub Pages is set up:

1. Test the frontend URL
2. Run backend locally or deploy it
3. Update CORS settings
4. Configure API URL for production
5. Share the GitHub Pages link!
