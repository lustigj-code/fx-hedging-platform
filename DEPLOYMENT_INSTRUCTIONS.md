# Quick Deployment Guide

Your code is ready to deploy! Everything is configured - you just need to complete one browser-based authentication.

## ✅ Already Completed

- ✅ Frontend deployed to Vercel: https://frontend-htjvjdcfu-lustigj-6781s-projects.vercel.app
- ✅ Code pushed to GitHub: https://github.com/lustigj-code/fx-hedging-platform
- ✅ All deployment configs created (Render, Railway, Docker)
- ✅ CORS configured for your Vercel frontend

## 🚀 Deploy Backend (2 minutes)

### Option 1: Render (Recommended - Free Tier Available)

1. Go to **https://render.com** and sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Select **"fx-hedging-platform"** repository
4. Render will auto-detect the configuration. Verify these settings:
   - **Name**: `fx-hedging-backend` (or your choice)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **"Create Web Service"**
6. Wait 2-3 minutes for deployment ☕
7. Copy your Render URL (will be like: `https://fx-hedging-backend.onrender.com`)

### Option 2: Railway

1. Go to **https://railway.app** and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select **"fx-hedging-platform"**
4. Click on the deployed service
5. Go to **Settings** → Set **Root Directory**: `backend`
6. Railway uses the `railway.json` config automatically
7. Copy your Railway URL from the deployment

## 🔗 Connect Frontend to Backend

After you get your backend URL, run these commands:

```bash
# Navigate to frontend
cd "/Users/juleslustig/Corporate FX Hedging/frontend"

# Add backend URL to Vercel environment variables
vercel env add VITE_API_URL production
# Paste your backend URL when prompted (e.g., https://fx-hedging-backend.onrender.com)

# Redeploy frontend with new backend URL
vercel --prod
```

## 🎉 Done!

Your platform will be fully deployed and live at:
- **Frontend**: https://frontend-htjvjdcfu-lustigj-6781s-projects.vercel.app
- **Backend**: [Your Render/Railway URL]
- **GitHub**: https://github.com/lustigj-code/fx-hedging-platform

## 🔧 Optional: Auto-Deploy on Push

To set up automatic deployments when you push code:

1. Get your Render API key from **Account Settings** → **API Keys**
2. Get your service ID from the Render dashboard URL
3. Add GitHub secrets:
   - Go to GitHub repo → **Settings** → **Secrets** → **Actions**
   - Add `RENDER_API_KEY` and `RENDER_SERVICE_ID`
4. Push code → Auto-deploys! 🚀

## Need Help?

The GitHub Action is already configured in `.github/workflows/deploy-render.yml` for auto-deployment once you add the secrets.
