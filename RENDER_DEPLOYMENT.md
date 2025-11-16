# Deploying to Render.com - Complete Guide

This guide explains how to deploy the Forex Trading Signals API to Render.com instead of Vercel.

## 📋 Differences from Vercel

| Aspect | Vercel | Render.com |
|--------|--------|------------|
| **Configuration File** | `vercel.json` | `render.yaml` or manual setup |
| **Entry Point** | `api/index.py` | `app.py` directly |
| **Server** | Serverless functions | Traditional web service |
| **WSGI Server** | Automatic | Gunicorn (recommended) |
| **Port** | Automatic | Uses `PORT` environment variable |

## 🚀 Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**:
```bash
git add .
git commit -m "Add Render.com deployment configuration"
git push origin main
```

2. **Create a Render Account**:
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (recommended for easy integration)

3. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to deploy

4. **Wait for Deployment**:
   - Render will build and deploy your application
   - You'll see build logs in real-time
   - Once deployed, you'll get a URL like: `https://your-app.onrender.com`

### Option 2: Manual Configuration

If you prefer to configure manually:

1. **Create a New Web Service** in Render dashboard

2. **Configure the Service**:
   - **Name**: `forex-trading-signals-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` or `gunicorn app:app --config gunicorn_config.py`
   - **Health Check Path**: `/api/health`

3. **Set Environment Variables** (if needed):
   - `PYTHON_VERSION`: `3.11.0` (optional)
   - `PORT`: Automatically set by Render (don't override)

4. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy

## 📁 Files Added for Render.com

### 1. `Procfile`
```
web: gunicorn app:app
```
- Tells Render how to start your application
- Uses Gunicorn (production WSGI server) instead of Flask's development server

### 2. `render.yaml`
- Configuration file for Render.com
- Defines build and start commands
- Sets up health checks
- Optional but recommended

### 3. `gunicorn_config.py`
- Gunicorn configuration file
- Optimizes worker processes
- Configures logging
- Can be used with: `gunicorn app:app --config gunicorn_config.py`

### 4. Updated `requirements.txt`
- Added `gunicorn==21.2.0` for production server

## ⚙️ Configuration Details

### Port Configuration

The `app.py` already handles the PORT environment variable:
```python
port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)
```

Render automatically sets the `PORT` environment variable, so your app will work without changes.

### Using Gunicorn

**Why Gunicorn?**
- Flask's development server is not suitable for production
- Gunicorn is a production-ready WSGI server
- Handles multiple requests efficiently
- Better performance and stability

**Start Commands**:
- Simple: `gunicorn app:app`
- With config: `gunicorn app:app --config gunicorn_config.py`
- Custom workers: `gunicorn app:app --workers 2`

### Health Check

Render uses `/api/health` to verify your app is running. This endpoint is already implemented in `app.py`.

## 🔧 Troubleshooting

### Issue: Build Fails

**Solution**:
1. Check build logs in Render dashboard
2. Ensure all dependencies are in `requirements.txt`
3. Verify Python version compatibility
4. Check for any import errors

### Issue: App Crashes on Start

**Possible Causes**:
1. Port not configured correctly
2. Missing dependencies
3. Import errors

**Solution**:
- Verify `app.py` uses `os.environ.get('PORT', 5000)`
- Check that all imports work
- Review error logs in Render dashboard

### Issue: 502 Bad Gateway

**Possible Causes**:
1. App not binding to `0.0.0.0`
2. Wrong port configuration
3. App crashing on startup

**Solution**:
- Ensure `app.run(host='0.0.0.0', port=port)` in `app.py`
- Check Render logs for errors
- Verify health check endpoint works

### Issue: Memory Limits (Free Tier)

**Solution**:
- Reduce Gunicorn workers in `gunicorn_config.py`:
  ```python
  workers = 2  # Instead of auto-calculated
  ```
- Or use simple start command: `gunicorn app:app --workers 2`

## 📊 Render.com Plans

### Free Tier
- **Limitations**:
  - Spins down after 15 minutes of inactivity
  - Limited resources (512MB RAM)
  - Slower cold starts
- **Best for**: Development, testing, low traffic

### Starter Plan ($7/month)
- Always on
- 512MB RAM
- Better performance

### Standard Plan ($25/month)
- More resources
- Better for production

## 🔄 Updating Your Deployment

### Automatic Deployments
- Render automatically deploys when you push to the connected branch (usually `main`)
- You can disable this in service settings

### Manual Deployments
1. Go to your service in Render dashboard
2. Click "Manual Deploy"
3. Select the branch/commit to deploy

## 🌐 Accessing Your API

Once deployed, your API will be available at:
- **Base URL**: `https://your-app-name.onrender.com/api`
- **Swagger UI**: `https://your-app-name.onrender.com/swagger/`
- **Health Check**: `https://your-app-name.onrender.com/api/health`

### Example Requests

```bash
# Health check
curl https://your-app-name.onrender.com/api/health

# Get TradingView signals
curl https://your-app-name.onrender.com/api/tradingview/signals/EURUSD?interval=5min

# Get aggregated signals
curl https://your-app-name.onrender.com/api/aggregated/signals/EURUSD
```

## 🔐 Environment Variables

If you need to set environment variables (like API keys):

1. Go to your service in Render dashboard
2. Navigate to "Environment" tab
3. Add variables:
   - `TWELVE_DATA_API_KEY`: Your Twelve Data API key
   - `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key (if you have one)
   - Any other variables your app needs

## 📝 Notes

### Vercel vs Render

**Keep Both Configurations**:
- You can keep both `vercel.json` and `render.yaml`
- They don't conflict
- Deploy to whichever platform you prefer

**Files You Can Remove** (if only using Render):
- `api/index.py` - Only needed for Vercel
- `vercel.json` - Only needed for Vercel

**Files You Need** (for Render):
- `Procfile` - Required for Render
- `requirements.txt` - Required (already exists)
- `app.py` - Required (already exists)
- `render.yaml` - Optional but recommended

### Development vs Production

**Local Development**:
```bash
python app.py
# Uses Flask development server
```

**Production (Render)**:
```bash
gunicorn app:app
# Uses Gunicorn production server
```

## ✅ Checklist

Before deploying to Render:

- [ ] All dependencies in `requirements.txt`
- [ ] `Procfile` exists with correct start command
- [ ] `app.py` uses `PORT` environment variable
- [ ] `app.py` binds to `0.0.0.0`
- [ ] Health check endpoint works (`/api/health`)
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Repository connected to Render

## 🎉 You're Ready!

Your application is now configured for Render.com deployment. Just push to GitHub and connect to Render!

---

**Need Help?**
- Check Render documentation: https://render.com/docs
- Review build logs in Render dashboard
- Check application logs for runtime errors

