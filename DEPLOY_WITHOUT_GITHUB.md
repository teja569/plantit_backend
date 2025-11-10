# Deploying to Render Without GitHub

This guide shows you how to deploy your FastAPI application to Render without using GitHub.

## Option 1: Using Render CLI (Recommended)

### Step 1: Install Render CLI

```bash
# Install via npm (requires Node.js)
npm install -g render-cli

# Or via Homebrew (macOS)
brew install render

# Or download from: https://github.com/renderinc/cli
```

### Step 2: Login to Render

```bash
render login
```

This will open your browser to authenticate.

### Step 3: Deploy from Local Directory

```bash
# Navigate to your project directory
cd /path/to/nexus

# Deploy using render.yaml
render deploy
```

### Step 4: Set Environment Variables

After deployment, set environment variables via Render Dashboard or CLI:

```bash
# Set environment variables via CLI
render env:set SECRET_KEY="your-secret-key"
render env:set DATABASE_URL="your-database-url"
render env:set GEMINI_API_KEY="your-api-key"
render env:set ALLOWED_ORIGINS="https://yourdomain.com"
```

## Option 2: Manual Deployment via Render Dashboard

### Step 1: Create Web Service Manually

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository" or "Deploy existing image"
4. If you don't have Git, choose "Deploy existing image" or use the manual option

### Step 2: Manual Configuration

If Render doesn't support direct upload, you can:

1. **Use GitLab or Bitbucket** (free alternatives to GitHub):
   - Push your code to GitLab or Bitbucket
   - Connect Render to that repository
   - Follow the same process as GitHub

2. **Use Render's Manual Deploy**:
   - Create a zip file of your project
   - Some platforms allow manual upload (check Render docs)

## Option 3: Using GitLab (Free Alternative)

### Step 1: Create GitLab Account

1. Go to https://gitlab.com
2. Sign up for free account

### Step 2: Create New Repository

1. Click "New project" → "Create blank project"
2. Name it (e.g., "nexus-api")
3. Don't initialize with README

### Step 3: Push Your Code

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Render deployment"

# Add GitLab remote
git remote add origin https://gitlab.com/yourusername/nexus-api.git

# Push to GitLab
git push -u origin main
```

### Step 4: Connect to Render

1. In Render Dashboard → "New +" → "Web Service"
2. Connect to GitLab
3. Select your repository
4. Render will auto-detect `render.yaml`

## Option 4: Using Render CLI with Direct Deploy

### Create a Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash
# Deploy to Render using CLI

echo "🚀 Deploying to Render..."

# Login (if not already)
render login

# Deploy
render deploy --service your-service-name

echo "✅ Deployment complete!"
```

## Quick Start: Render CLI Method

### 1. Install Render CLI

```bash
npm install -g render-cli
```

### 2. Login

```bash
render login
```

### 3. Create Service (First Time)

```bash
# Create service from render.yaml
render services:create --config render.yaml
```

### 4. Deploy Updates

```bash
# Deploy from current directory
render deploy
```

## Environment Variables Setup

After creating the service, set environment variables:

### Via CLI:
```bash
render env:set SECRET_KEY="your-secret-key-here"
render env:set DATABASE_URL="postgresql://user:pass@host:port/db"
render env:set GEMINI_API_KEY="your-gemini-key"
render env:set ALLOWED_ORIGINS="https://yourdomain.com,http://localhost:3000"
render env:set DEBUG="False"
```

### Via Dashboard:
1. Go to Render Dashboard
2. Select your service
3. Go to "Environment" tab
4. Add each variable

## Required Environment Variables

- `SECRET_KEY` - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `DATABASE_URL` or `PRISMA_DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `ALLOWED_ORIGINS` - Comma-separated CORS origins
- `DEBUG` - Set to `False` for production

## Troubleshooting

### Render CLI Not Found
```bash
# Make sure Node.js is installed
node --version

# Install Render CLI
npm install -g render-cli
```

### Authentication Issues
```bash
# Re-authenticate
render logout
render login
```

### Deployment Fails
- Check Render logs in dashboard
- Verify all environment variables are set
- Ensure `render.yaml` is correct
- Check that `requirements.txt` is valid

## Alternative: Use Docker

If you prefer Docker deployment:

1. Create `Dockerfile` (if not exists)
2. Build and push to Docker Hub
3. Deploy from Docker image in Render

## Next Steps

1. Choose your deployment method
2. Set up environment variables
3. Deploy your service
4. Test the `/health` endpoint
5. Update your frontend to use the new API URL

For more help, visit: https://render.com/docs

