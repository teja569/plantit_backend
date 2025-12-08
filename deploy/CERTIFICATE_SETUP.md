# SSL Certificate Setup Guide

## Problem: ERR_CERT_AUTHORITY_INVALID

Browsers are rejecting the self-signed certificate with `ERR_CERT_AUTHORITY_INVALID`. This is expected behavior - browsers don't trust self-signed certificates for security reasons.

## Solution: Use Let's Encrypt (Free SSL Certificate)

You need a **domain name** pointing to your server IP (`3.111.165.191`).

### Option 1: Use Existing Domain

If you have a domain name:

1. **Point your domain to the server:**
   - Create an A record: `api.yourdomain.com` → `3.111.165.191`
   - Or use subdomain: `yourdomain.com` → `3.111.165.191`
   - Wait for DNS propagation (5-30 minutes)

2. **Run the setup script:**
   ```powershell
   .\deploy\setup-letsencrypt.ps1 -DomainName "api.yourdomain.com" -Email "your@email.com"
   ```

### Option 2: Get a Free Domain

If you don't have a domain, here are free options:

#### A. Freenom (Free .tk, .ml, .ga domains)
1. Go to https://www.freenom.com
2. Register a free domain
3. Point it to `3.111.165.191`
4. Run the setup script

#### B. DuckDNS (Free subdomain)
1. Go to https://www.duckdns.org
2. Create account and get subdomain (e.g., `yourapp.duckdns.org`)
3. Update DNS to point to `3.111.165.191`
4. Run the setup script

#### C. Cloudflare Tunnel (No domain needed!)
This is the easiest option - no domain required:

```bash
# On your server
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191

# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Run tunnel (follow prompts to create tunnel)
cloudflared tunnel --url http://localhost:8000
```

This will give you a `*.trycloudflare.com` URL with valid SSL!

### Option 3: Use Cloudflare Proxy (If you have a domain)

1. Add your domain to Cloudflare
2. Change nameservers to Cloudflare
3. Create A record: `api` → `3.111.165.191` (proxy enabled)
4. Cloudflare will provide SSL automatically!

## Quick Setup with Domain

```powershell
# Replace with your domain
.\deploy\setup-letsencrypt.ps1 -DomainName "api.yourdomain.com" -Email "admin@yourdomain.com"
```

## Manual Setup

If you prefer manual setup:

```bash
ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191

# Install certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Get certificate (replace with your domain)
sudo certbot certonly --standalone -d api.yourdomain.com --email admin@yourdomain.com --agree-tos

# Update nginx config
sudo nano /etc/nginx/sites-available/plant-delivery-api
# Update server_name and certificate paths

# Test and restart
sudo nginx -t
sudo systemctl start nginx
```

## Verify Certificate

```bash
# Check certificate
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run
```

## Update Admin Panel

After setting up the certificate, update your admin panel:

```javascript
// Change from:
const API_BASE_URL = 'https://3.111.165.191/api/v1';

// To:
const API_BASE_URL = 'https://api.yourdomain.com/api/v1';
```

## Troubleshooting

### DNS Not Propagated
- Wait 5-30 minutes after DNS changes
- Check DNS: `nslookup api.yourdomain.com`
- Should return `3.111.165.191`

### Port 80 Not Accessible
- Check firewall: `sudo ufw status`
- Ensure port 80 is open: `sudo ufw allow 80/tcp`
- Check AWS Security Group allows port 80

### Certificate Already Exists
- List certificates: `sudo certbot certificates`
- Delete if needed: `sudo certbot delete --cert-name api.yourdomain.com`

## Auto-Renewal

Certbot sets up auto-renewal automatically. Certificates expire every 90 days and auto-renew.

Check renewal status:
```bash
sudo systemctl status certbot.timer
```

