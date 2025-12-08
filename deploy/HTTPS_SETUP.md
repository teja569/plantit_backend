# HTTPS Setup Guide

## Problem

The admin panel is hosted on HTTPS (Vercel: `https://admin-panel-pink-nine.vercel.app`) but is trying to connect to the API server over HTTP (`http://3.111.165.191/api/v1`). Modern browsers block mixed content (HTTPS pages requesting HTTP resources) for security reasons.

## Solutions

### Option 1: Set up HTTPS on API Server (Recommended)

This is the proper solution. You have two options:

#### A. Using a Domain Name with Let's Encrypt (Best)

1. **Get a domain name** pointing to `3.111.165.191`
2. **Run the setup script**:
   ```bash
   # On Windows (PowerShell)
   .\deploy\setup-https.ps1
   
   # On Linux/Mac
   chmod +x deploy/setup-https.sh
   ./deploy/setup-https.sh
   ```
3. **Update admin panel** to use `https://yourdomain.com/api/v1`

#### B. Using Self-Signed Certificate (Quick Fix for Testing)

1. **Run the setup script** and choose self-signed certificate option
2. **Update admin panel** to use `https://3.111.165.191/api/v1`
3. **Note**: Browsers will show a security warning, but HTTPS will work

### Option 2: Update Admin Panel Configuration

If you have access to the admin panel code, update the API base URL:

**Before:**
```javascript
const API_BASE_URL = 'http://3.111.165.191/api/v1';
```

**After (with domain):**
```javascript
const API_BASE_URL = 'https://yourdomain.com/api/v1';
```

**After (with IP - self-signed cert):**
```javascript
const API_BASE_URL = 'https://3.111.165.191/api/v1';
```

## Manual Setup Steps

### 1. Install Certbot (for Let's Encrypt)

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

### 2. Get SSL Certificate

**With domain:**
```bash
sudo certbot certonly --standalone -d yourdomain.com --non-interactive --agree-tos --email your@email.com
```

**Self-signed (for testing):**
```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/selfsigned.key \
    -out /etc/nginx/ssl/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=3.111.165.191"
```

### 3. Update Nginx Configuration

```bash
# Copy HTTPS config
sudo cp deploy/nginx-https.conf /etc/nginx/sites-available/plant-delivery-api

# If using domain, update the domain name in the config
sudo nano /etc/nginx/sites-available/plant-delivery-api

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 4. Update Firewall Rules

Ensure ports 80 and 443 are open:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

## Verify HTTPS is Working

```bash
# Test HTTPS endpoint
curl https://3.111.165.191/health

# Or with domain
curl https://yourdomain.com/health
```

## Update Admin Panel

After setting up HTTPS, update your admin panel's API configuration:

1. Find the API base URL configuration (usually in `.env`, `config.js`, or environment variables)
2. Change from `http://` to `https://`
3. If using a domain, update the hostname
4. Redeploy the admin panel

## Troubleshooting

### Certificate Issues

- **Self-signed certificate warning**: This is expected. Click "Advanced" → "Proceed to site" in browser
- **Let's Encrypt validation failed**: Ensure domain DNS points to `3.111.165.191` and port 80 is accessible

### Nginx Issues

- **Configuration test fails**: Check certificate paths in nginx config
- **502 Bad Gateway**: Ensure the FastAPI app is running on port 8000

### CORS Issues

After enabling HTTPS, you may need to update CORS settings in `app/core/config.py`:

```python
allowed_origins = "https://admin-panel-pink-nine.vercel.app"
```

## Quick Reference

**Current API URL (HTTP):**
- `http://3.111.165.191/api/v1`

**After HTTPS Setup:**
- `https://3.111.165.191/api/v1` (self-signed)
- `https://yourdomain.com/api/v1` (Let's Encrypt)

**Admin Panel URL:**
- `https://admin-panel-pink-nine.vercel.app/login`

