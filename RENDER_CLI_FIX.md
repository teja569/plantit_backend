# Fix: Render CLI Package Conflict

The `render-cli` npm package is a **templating engine**, not the Render deployment CLI!

## The Problem

The npm package `render-cli` is actually a templating engine tool, not the official Render.com CLI. This causes conflicts.

## Solution: Use Render Dashboard Instead (Recommended)

Since the CLI has package conflicts, **deploy directly via Render Dashboard**:

### Step 1: Create Web Service in Dashboard

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Choose **"Deploy existing image"** or **"Build and deploy from a Git repository"**

### Step 2: Manual Configuration

If you don't have Git, use **"Deploy existing image"** or configure manually:

**Service Settings:**
- **Name**: `plant-delivery-api`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

### Step 3: Set Environment Variables

In Render Dashboard → Your Service → Environment:

```
SECRET_KEY = [generate: python -c "import secrets; print(secrets.token_urlsafe(32))"]
DATABASE_URL = [your PostgreSQL connection string]
GEMINI_API_KEY = [your API key]
ALLOWED_ORIGINS = https://yourdomain.com,http://localhost:3000
DEBUG = False
PYTHON_VERSION = 3.11.0
PYTHONUNBUFFERED = 1
```

### Step 4: Deploy

Click **"Create Web Service"** and Render will deploy your app.

## Alternative: Use GitLab (Free, No GitHub Needed)

### Step 1: Create GitLab Account

1. Go to https://gitlab.com
2. Sign up (free)

### Step 2: Create Repository

1. Click **"New project"** → **"Create blank project"**
2. Name it (e.g., `nexus-api`)
3. Don't initialize with README

### Step 3: Push Your Code

```powershell
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Render"

# Add GitLab remote
git remote add origin https://gitlab.com/yourusername/nexus-api.git

# Push to GitLab
git push -u origin main
```

### Step 4: Connect to Render

1. In Render Dashboard → **"New +"** → **"Web Service"**
2. Connect to **GitLab**
3. Select your repository
4. Render will auto-detect `render.yaml`
5. Set environment variables
6. Deploy!

## Alternative: Use Render API

You can also deploy via Render's REST API using curl or PowerShell:

```powershell
# Get API key from: https://dashboard.render.com/account/api-keys
$API_KEY = "your-api-key"
$SERVICE_ID = "your-service-id"

# Deploy via API
Invoke-RestMethod -Uri "https://api.render.com/v1/services/$SERVICE_ID/deploys" `
  -Method Post `
  -Headers @{"Authorization" = "Bearer $API_KEY"} `
  -ContentType "application/json"
```

## Recommended: Dashboard Method

**The easiest way without CLI is to use the Render Dashboard directly:**

1. ✅ No package conflicts
2. ✅ Visual interface
3. ✅ Easy environment variable management
4. ✅ Built-in logs and monitoring
5. ✅ Works immediately

Just go to https://dashboard.render.com and create a new Web Service manually using the settings from `render.yaml`.

## Next Steps

1. **Use Render Dashboard** (easiest, no CLI needed)
2. **Or use GitLab** + Render Dashboard (if you want Git integration)
3. **Or use Render API** (if you need automation)

The Dashboard method is the most reliable and doesn't require any CLI tools!

