# Quick Deploy to Render (Without GitHub)

## Fastest Method: Render CLI

### 1. Install Render CLI

**Windows (PowerShell):**
```powershell
npm install -g render-cli
```

**macOS/Linux:**
```bash
npm install -g render-cli
```

*Note: Requires Node.js. Download from https://nodejs.org if needed.*

### 2. Login to Render

**If you have conflicts, use npx (recommended):**
```bash
npx render-cli login
```

**Or if render-cli is installed:**
```bash
render-cli login
```

This opens your browser for authentication.

### 3. Create Service (First Time Only)

**Using npx (recommended):**
```bash
npx render-cli services:create --config render.yaml
```

**Or if render-cli is installed:**
```bash
render-cli services:create --config render.yaml
```

This creates the service from `render.yaml`.

### 4. Set Environment Variables

**Via Dashboard (Easier):**
1. Go to https://dashboard.render.com
2. Click your service
3. Go to "Environment" tab
4. Add these variables:

```
SECRET_KEY = [generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
DATABASE_URL = [your PostgreSQL connection string]
GEMINI_API_KEY = [your Gemini API key]
ALLOWED_ORIGINS = https://yourdomain.com,http://localhost:3000
DEBUG = False
```

**Via CLI (using npx):**
```bash
npx render-cli env:set SECRET_KEY="your-secret-key"
npx render-cli env:set DATABASE_URL="postgresql://user:pass@host:port/db"
npx render-cli env:set GEMINI_API_KEY="your-key"
npx render-cli env:set ALLOWED_ORIGINS="https://yourdomain.com"
npx render-cli env:set DEBUG="False"
```

### 5. Deploy

**Using npx (recommended):**
```bash
npx render-cli deploy
```

**Or if render-cli is installed:**
```bash
render-cli deploy
```

That's it! Your service will be deployed.

## Alternative: Use Scripts

### Windows:
```powershell
.\deploy.bat
```

### macOS/Linux:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Verify Deployment

1. Check your service URL in Render Dashboard
2. Test: `https://your-service.onrender.com/health`
3. Should return: `{"status": "healthy", ...}`

## Update Deployment

To update your code:

```bash
# Make your changes
# Then deploy again
render deploy
```

## Troubleshooting

**CLI not found:**
- Install Node.js: https://nodejs.org
- Then: `npm install -g render-cli`

**Login issues:**
```bash
npx render-cli logout
npx render-cli login
```

**Command conflicts:**
If `render` doesn't work, use `npx render-cli` or `render-cli` instead.

**Deployment fails:**
- Check Render Dashboard → Logs
- Verify all environment variables are set
- Ensure `requirements.txt` is valid

## Need Help?

- Render Docs: https://render.com/docs
- Render CLI: https://github.com/renderinc/cli
- Check `DEPLOY_WITHOUT_GITHUB.md` for detailed instructions

