# Deploying to Render

This guide will help you deploy the Plant Delivery API to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. A Prisma Postgres database (or any PostgreSQL database)
3. Your environment variables ready

## Step 1: Create a New Web Service on Render

1. Go to your Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the configuration from `render.yaml`

## Step 2: Configure Environment Variables

In Render Dashboard → Your Service → Environment, add:

### Required Variables:
- `SECRET_KEY` - Generate a secure key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `DATABASE_URL` or `PRISMA_DATABASE_URL` - Your PostgreSQL connection string
- `GEMINI_API_KEY` - Your Google Gemini API key
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins (e.g., `https://yourdomain.com,https://www.yourdomain.com`)

### Optional Variables:
- `DEBUG` - Set to `False` for production (default: `False`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `FRONTEND_URL` - Your frontend URL
- `RATE_LIMIT_PER_MINUTE` - Rate limit (default: 60)

## Step 3: Database Setup

### Using Prisma Postgres:
1. In Render Dashboard, create a new PostgreSQL database
2. Or use your existing Prisma Postgres database
3. Copy the connection string to `DATABASE_URL` or `PRISMA_DATABASE_URL`

### Database URL Format:
```
postgresql://user:password@host:port/dbname?sslmode=require
```

## Step 4: Deploy

1. Render will automatically deploy when you push to the main branch
2. Or manually trigger a deployment from the Render Dashboard
3. Check the logs to ensure the service starts correctly

## Step 5: Verify Deployment

1. Visit your service URL (provided by Render)
2. Check `/health` endpoint: `https://your-service.onrender.com/health`
3. Check root endpoint: `https://your-service.onrender.com/`

## Configuration Files

- `render.yaml` - Render service configuration
- `start.sh` - Startup script (optional, Render uses `render.yaml` startCommand)
- `requirements.txt` - Python dependencies

## Troubleshooting

### Service won't start:
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `DATABASE_URL` is correct and accessible

### Database connection errors:
- Verify `DATABASE_URL` format (must be `postgresql://` not `postgres://`)
- Check if database allows connections from Render IPs
- Ensure SSL is enabled (`sslmode=require`)

### 500 Internal Server Error:
- Check Render logs for detailed error messages
- Verify `SECRET_KEY` is set
- Check database connection

## Custom Domain

1. In Render Dashboard → Your Service → Settings
2. Add your custom domain
3. Update `ALLOWED_ORIGINS` to include your custom domain

## Monitoring

- View logs in Render Dashboard → Your Service → Logs
- Set up alerts in Render Dashboard → Your Service → Alerts
- Monitor metrics in Render Dashboard → Your Service → Metrics

## Cost

- **Starter Plan**: Free tier available (spins down after inactivity)
- **Standard Plan**: $7/month (always on)
- **Pro Plan**: $25/month (better performance)

For production, consider the Standard or Pro plan to avoid cold starts.

