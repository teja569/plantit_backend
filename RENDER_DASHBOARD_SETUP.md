# Deploy to Render via Dashboard (No CLI Needed)

Since the CLI has package conflicts, use the Render Dashboard directly. It's actually easier!

## Step-by-Step Dashboard Deployment

### Step 1: Create Account & Service

1. Go to https://dashboard.render.com
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**

### Step 2: Connect Repository (Optional)

**Option A: Use GitLab (Free, No GitHub)**
1. Click **"Connect account"** → **"GitLab"**
2. Authorize Render to access GitLab
3. Select your repository
4. Skip to Step 4

**Option B: Manual Setup (No Git)**
1. Click **"Deploy existing image"** or **"Manual"**
2. Continue to Step 3

### Step 3: Manual Configuration (If No Git)

Fill in these settings:

**Basic Settings:**
- **Name**: `plant-delivery-api`
- **Region**: Choose closest to you
- **Branch**: `main` (if using Git) or leave blank

**Build & Deploy:**
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Health Check:**
- **Health Check Path**: `/health`

**Plan:**
- **Starter** (Free, spins down after inactivity)
- **Standard** ($7/month, always on)
- **Pro** ($25/month, better performance)

### Step 4: Set Environment Variables

Before deploying, go to **"Environment"** tab and add:

```
SECRET_KEY = [generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
DATABASE_URL = postgresql://user:password@host:port/dbname?sslmode=require
GEMINI_API_KEY = your-gemini-api-key
ALLOWED_ORIGINS = https://yourdomain.com,http://localhost:3000
DEBUG = False
PYTHON_VERSION = 3.11.0
PYTHONUNBUFFERED = 1
```

**Important:**
- Replace `DATABASE_URL` with your actual Prisma Postgres connection string
- Generate a secure `SECRET_KEY`
- Add your frontend URLs to `ALLOWED_ORIGINS`

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Install dependencies from `requirements.txt`
   - Start your FastAPI app
   - Make it available at `https://your-service.onrender.com`

### Step 6: Verify

1. Wait for deployment to complete (2-5 minutes)
2. Check **"Logs"** tab for any errors
3. Test: `https://your-service.onrender.com/health`
4. Should return: `{"status": "healthy", ...}`

## Updating Your Deployment

### If Using Git (GitLab):
1. Make changes locally
2. Commit: `git commit -m "Update"`
3. Push: `git push origin main`
4. Render auto-deploys

### If Manual:
1. Make changes locally
2. In Render Dashboard → **"Manual Deploy"**
3. Upload your updated files (or use GitLab)

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ Yes | Secret key for JWT tokens |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string |
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key |
| `ALLOWED_ORIGINS` | ✅ Yes | Comma-separated CORS origins |
| `DEBUG` | ❌ No | Set to `False` for production |
| `PYTHON_VERSION` | ❌ No | Python version (default: 3.11.0) |
| `PYTHONUNBUFFERED` | ❌ No | Set to `1` for better logs |

## Troubleshooting

### Service Won't Start
- Check **Logs** tab for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is valid
- Check `DATABASE_URL` is correct

### Database Connection Errors
- Verify `DATABASE_URL` format: `postgresql://` (not `postgres://`)
- Check database allows connections from Render
- Ensure SSL is enabled: `?sslmode=require`

### 500 Internal Server Error
- Check Render logs for detailed error
- Verify `SECRET_KEY` is set
- Test `/health` endpoint first

## Custom Domain

1. In Render Dashboard → Your Service → **Settings**
2. Scroll to **"Custom Domains"**
3. Add your domain
4. Update `ALLOWED_ORIGINS` to include your domain

## Monitoring

- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Request metrics
- **Alerts**: Set up email alerts for errors

## Cost

- **Starter**: Free (spins down after 15 min inactivity)
- **Standard**: $7/month (always on, better for production)
- **Pro**: $25/month (best performance)

For production, consider Standard plan to avoid cold starts.

## Need Help?

- Render Docs: https://render.com/docs
- Render Support: https://render.com/support
- Check your service logs in Dashboard

