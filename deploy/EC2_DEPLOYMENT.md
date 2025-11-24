# EC2 Server Deployment Guide

This guide will help you deploy the Plant Delivery API to an EC2 Ubuntu server.

## Server Details

- **IP Address**: 3.111.165.191
- **User**: ubuntu
- **SSH Key**: ~/.ssh/AWS.pem

## Prerequisites

1. SSH key file at `~/.ssh/AWS.pem`
2. SSH access to the server
3. Server should be running Ubuntu 20.04 or later

## Quick Deployment

### Step 1: Setup Server (First Time Only)

```bash
chmod +x deploy/setup-server.sh
./deploy/setup-server.sh
```

This will install:
- Python 3.11
- PostgreSQL client
- Nginx
- Node.js
- Required system dependencies

### Step 2: Create .env File on Server

SSH into the server and create the `.env` file:

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191

# Create .env file
sudo nano /opt/plant-delivery-api/.env
```

Add your environment variables:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# Security
SECRET_KEY=your-super-secret-key-here

# API Keys
GEMINI_API_KEY=your-gemini-api-key

# AWS (if using S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# CORS
ALLOWED_ORIGINS=*

# Environment
DEBUG=False
ENABLE_DOCS=True
LOG_LEVEL=INFO
```

Save and exit (Ctrl+X, Y, Enter)

### Step 3: Deploy Application

```bash
chmod +x deploy/ec2-deploy.sh
export SSH_KEY=~/.ssh/AWS.pem
export SSH_USER=ubuntu
export SSH_HOST=3.111.165.191
./deploy/ec2-deploy.sh
```

This will:
1. Copy application files to server
2. Set up Python virtual environment
3. Install dependencies
4. Configure systemd service
5. Configure Nginx
6. Run database migrations
7. Start the service

## Production URLs

After deployment, your API will be available at:

- **API Base URL**: `http://3.111.165.191/api/v1`
- **Health Check**: `http://3.111.165.191/health`
- **API Documentation**: `http://3.111.165.191/docs`
- **ReDoc**: `http://3.111.165.191/redoc`

## Service Management

### Check Service Status

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
sudo systemctl status plant-delivery-api
```

### View Logs

```bash
# Application logs
sudo journalctl -u plant-delivery-api -f

# Nginx logs
sudo tail -f /var/log/nginx/plant-delivery-api-access.log
sudo tail -f /var/log/nginx/plant-delivery-api-error.log
```

### Restart Service

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
sudo systemctl restart plant-delivery-api
sudo systemctl restart nginx
```

### Stop Service

```bash
sudo systemctl stop plant-delivery-api
```

### Start Service

```bash
sudo systemctl start plant-delivery-api
```

## Database Migrations

Run migrations manually:

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
cd /opt/plant-delivery-api
source venv/bin/activate
export $(cat .env | xargs)
alembic upgrade head
```

## Updating Application

To update the application:

```bash
./deploy/ec2-deploy.sh
```

This will:
- Copy new files
- Install/update dependencies
- Restart the service

## Nginx Configuration

Nginx is configured as a reverse proxy. Configuration file:
- `/etc/nginx/sites-available/plant-delivery-api`

To reload Nginx after changes:

```bash
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

## SSL/HTTPS Setup (Optional)

To enable HTTPS with Let's Encrypt:

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
```

## Monitoring

### Check Application Health

```bash
curl http://3.111.165.191/health
```

### Check Service Status

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
sudo systemctl status plant-delivery-api
```

### Monitor Resource Usage

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Application logs
sudo journalctl -u plant-delivery-api --since "1 hour ago"
```

## Troubleshooting

### Service Won't Start

1. Check logs:
   ```bash
   sudo journalctl -u plant-delivery-api -n 50
   ```

2. Check environment variables:
   ```bash
   sudo systemctl cat plant-delivery-api
   ```

3. Test manually:
   ```bash
   cd /opt/plant-delivery-api
   source venv/bin/activate
   export $(cat .env | xargs)
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Database Connection Issues

1. Verify database URL in `.env`
2. Check network connectivity:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

### Nginx Issues

1. Test configuration:
   ```bash
   sudo nginx -t
   ```

2. Check error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Permission Issues

```bash
sudo chown -R ubuntu:ubuntu /opt/plant-delivery-api
sudo chmod +x /opt/plant-delivery-api/venv/bin/*
```

## Security Recommendations

1. **Enable Firewall**:
   ```bash
   sudo ufw status
   sudo ufw enable
   ```

2. **Set up SSL/HTTPS** (see SSL Setup above)

3. **Keep system updated**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

4. **Use strong passwords** for database and secrets

5. **Restrict SSH access** (use key-based auth only)

6. **Regular backups** of database and application

## Backup

### Database Backup

```bash
# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_YYYYMMDD.sql
```

### Application Backup

```bash
# Backup application directory
tar -czf app_backup_$(date +%Y%m%d).tar.gz /opt/plant-delivery-api
```

## Scaling

### Increase Workers

Edit `/etc/systemd/system/plant-delivery-api.service`:

```ini
ExecStart=/opt/plant-delivery-api/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 8 \
    --log-level info
```

Then restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart plant-delivery-api
```

### Load Balancing

For multiple servers, set up a load balancer (AWS ALB, Nginx, etc.) in front of multiple EC2 instances.

## Maintenance

### Update Dependencies

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
cd /opt/plant-delivery-api
source venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart plant-delivery-api
```

### Update Application Code

```bash
./deploy/ec2-deploy.sh
```

## Production Checklist

- [ ] Server setup completed
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Service is running
- [ ] Nginx is configured
- [ ] Health check passes
- [ ] SSL certificate installed (if using domain)
- [ ] Firewall configured
- [ ] Backups configured
- [ ] Monitoring set up

## Support

For issues:
1. Check service logs: `sudo journalctl -u plant-delivery-api`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/plant-delivery-api-error.log`
3. Test health endpoint: `curl http://3.111.165.191/health`
4. Verify environment variables are set correctly

