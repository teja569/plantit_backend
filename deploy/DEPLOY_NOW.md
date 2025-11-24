# Quick Deployment Guide

## Prerequisites

1. **SSH Key**: Place your `AWS.pem` file at one of these locations:
   - `C:\Users\ADMIN\.ssh\AWS.pem` (Windows default)
   - Or specify the path when running the script

2. **SSH Access**: Ensure you can connect to the server:
   ```powershell
   ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191
   ```

## Deployment Steps

### Option 1: Using PowerShell Script (Recommended)

```powershell
# If key is at default location
powershell -ExecutionPolicy Bypass -File deploy/ec2-deploy.ps1

# If key is at custom location
powershell -ExecutionPolicy Bypass -File deploy/ec2-deploy.ps1 -SSHKey "C:\path\to\AWS.pem"
```

### Option 2: Manual Deployment

1. **Copy SSH key to server** (if needed):
   ```powershell
   scp -i C:\Users\ADMIN\.ssh\AWS.pem C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191:~/.ssh/
   ```

2. **SSH into server**:
   ```powershell
   ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191
   ```

3. **On the server, run**:
   ```bash
   # Setup server
   sudo apt-get update -y
   sudo apt-get install -y python3.11 python3.11-venv python3-pip python3-dev
   sudo apt-get install -y postgresql-client libpq-dev build-essential nginx
   
   # Create app directory
   sudo mkdir -p /opt/plant-delivery-api
   sudo chown -R ubuntu:ubuntu /opt/plant-delivery-api
   ```

4. **Copy files from your local machine**:
   ```powershell
   # Copy .env file
   scp -i C:\Users\ADMIN\.ssh\AWS.pem .env ubuntu@3.111.165.191:/opt/plant-delivery-api/
   
   # Copy application files
   scp -i C:\Users\ADMIN\.ssh\AWS.pem -r app ubuntu@3.111.165.191:/opt/plant-delivery-api/
   scp -i C:\Users\ADMIN\.ssh\AWS.pem main.py requirements.txt alembic.ini ubuntu@3.111.165.191:/opt/plant-delivery-api/
   scp -i C:\Users\ADMIN\.ssh\AWS.pem -r alembic ubuntu@3.111.165.191:/opt/plant-delivery-api/
   ```

5. **On server, setup and start**:
   ```bash
   cd /opt/plant-delivery-api
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Copy service files
   sudo cp deploy/plant-delivery-api.service /etc/systemd/system/
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/plant-delivery-api
   sudo ln -s /etc/nginx/sites-available/plant-delivery-api /etc/nginx/sites-enabled/
   
   # Start services
   sudo systemctl daemon-reload
   sudo systemctl enable plant-delivery-api
   sudo systemctl start plant-delivery-api
   sudo systemctl restart nginx
   ```

## After Deployment

Your API will be available at:
- **API Base**: http://3.111.165.191/api/v1
- **Health Check**: http://3.111.165.191/health
- **API Docs**: http://3.111.165.191/docs

## Troubleshooting

### SSH Key Permission Issues

On Windows, you may need to set permissions:
```powershell
icacls "C:\Users\ADMIN\.ssh\AWS.pem" /inheritance:r
icacls "C:\Users\ADMIN\.ssh\AWS.pem" /grant:r "$env:USERNAME:(R)"
```

### Connection Issues

Test SSH connection first:
```powershell
ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 "echo 'Connected'"
```

### Service Not Starting

SSH into server and check logs:
```bash
sudo journalctl -u plant-delivery-api -f
```

