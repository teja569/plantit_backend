# PowerShell deployment script for EC2
param(
    [string]$SSHKey = "$env:USERPROFILE\.ssh\AWS.pem",
    [string]$SSHUser = "ubuntu",
    [string]$SSHHost = "3.111.165.191"
)

$ErrorActionPreference = "Stop"

Write-Host "Starting EC2 deployment..." -ForegroundColor Green
Write-Host "Server: ${SSHUser}@${SSHHost}" -ForegroundColor Yellow

# Check if SSH key exists
if (-not (Test-Path $SSHKey)) {
    Write-Host "Error: SSH key not found at $SSHKey" -ForegroundColor Red
    exit 1
}

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Green
$testResult = ssh -i $SSHKey -o StrictHostKeyChecking=no "${SSHUser}@${SSHHost}" "echo 'Connection successful'" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot connect to server" -ForegroundColor Red
    Write-Host $testResult
    exit 1
}

# Setup server (first time)
Write-Host "Setting up server..." -ForegroundColor Green
$setupScript = @"
#!/bin/bash
set -e
echo 'Updating system packages...'
sudo apt-get update -y

echo 'Installing Python and dependencies...'
sudo apt-get install -y python3 python3-venv python3-pip python3-dev
sudo apt-get install -y postgresql-client libpq-dev build-essential
sudo apt-get install -y nginx supervisor curl git

echo 'Creating application directory...'
sudo mkdir -p /opt/plant-delivery-api
sudo mkdir -p /opt/plant-delivery-api/logs
sudo mkdir -p /opt/plant-delivery-api/models
sudo chown -R ubuntu:ubuntu /opt/plant-delivery-api

echo 'Setting up firewall...'
sudo ufw --force enable || true
sudo ufw allow 22/tcp || true
sudo ufw allow 80/tcp || true
sudo ufw allow 443/tcp || true

echo 'Server setup completed!'
"@

# Write script to temp file and execute
$tempScript = [System.IO.Path]::GetTempFileName()
$setupScript | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline
scp -i $SSHKey $tempScript "${SSHUser}@${SSHHost}:/tmp/setup.sh"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "chmod +x /tmp/setup.sh && bash /tmp/setup.sh"
Remove-Item $tempScript

# Copy .env file
Write-Host "Copying .env file..." -ForegroundColor Green
if (Test-Path ".env") {
    scp -i $SSHKey ".env" "${SSHUser}@${SSHHost}:/tmp/.env"
    ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo mv /tmp/.env /opt/plant-delivery-api/.env && sudo chown ubuntu:ubuntu /opt/plant-delivery-api/.env"
} else {
    Write-Host "Warning: .env file not found. Please create it on the server manually." -ForegroundColor Yellow
}

# Copy application files using rsync (if available) or scp
Write-Host "Copying application files..." -ForegroundColor Green

# Create temporary exclude file
$excludeFile = [System.IO.Path]::GetTempFileName()
@"
venv
__pycache__
*.pyc
.git
*.db
*.log
node_modules
.env
.venv
*.pem
*.key
"@ | Out-File -FilePath $excludeFile -Encoding ASCII

# Copy files
$filesToCopy = @(
    "app",
    "alembic",
    "alembic.ini",
    "main.py",
    "requirements.txt"
)

foreach ($item in $filesToCopy) {
    if (Test-Path $item) {
        Write-Host "Copying $item..." -ForegroundColor Yellow
        if ($item -eq "app" -or $item -eq "alembic") {
            # Directory
            scp -i $SSHKey -r $item "${SSHUser}@${SSHHost}:/opt/plant-delivery-api/"
        } else {
            # File
            scp -i $SSHKey $item "${SSHUser}@${SSHHost}:/opt/plant-delivery-api/"
        }
    }
}

# Remove temp file
Remove-Item $excludeFile

# Setup Python environment and install dependencies
Write-Host "Setting up Python environment..." -ForegroundColor Green
$pythonScript = @"
#!/bin/bash
cd /opt/plant-delivery-api
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
"@

$tempScript = [System.IO.Path]::GetTempFileName()
$pythonScript | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline
scp -i $SSHKey $tempScript "${SSHUser}@${SSHHost}:/tmp/setup-python.sh"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "chmod +x /tmp/setup-python.sh && bash /tmp/setup-python.sh"
Remove-Item $tempScript

# Copy systemd service file
Write-Host "Setting up systemd service..." -ForegroundColor Green
scp -i $SSHKey "deploy/plant-delivery-api.service" "${SSHUser}@${SSHHost}:/tmp/"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" @"
sudo mv /tmp/plant-delivery-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable plant-delivery-api
"@

# Copy nginx configuration
Write-Host "Setting up Nginx..." -ForegroundColor Green
scp -i $SSHKey "deploy/nginx.conf" "${SSHUser}@${SSHHost}:/tmp/plant-delivery-api-nginx.conf"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" @"
sudo mv /tmp/plant-delivery-api-nginx.conf /etc/nginx/sites-available/plant-delivery-api
sudo ln -sf /etc/nginx/sites-available/plant-delivery-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
"@

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Green
$migrationScript = @"
#!/bin/bash
cd /opt/plant-delivery-api
source venv/bin/activate
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi
alembic upgrade head || echo 'Migrations skipped or failed'
"@

$tempScript = [System.IO.Path]::GetTempFileName()
$migrationScript | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline
scp -i $SSHKey $tempScript "${SSHUser}@${SSHHost}:/tmp/run-migrations.sh"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "chmod +x /tmp/run-migrations.sh && bash /tmp/run-migrations.sh"
Remove-Item $tempScript

# Restart service
Write-Host "Restarting service..." -ForegroundColor Green
$restartScript = @"
#!/bin/bash
sudo systemctl restart plant-delivery-api || true
sleep 3
sudo systemctl status plant-delivery-api --no-pager || true
"@

$tempScript = [System.IO.Path]::GetTempFileName()
$restartScript | Out-File -FilePath $tempScript -Encoding ASCII -NoNewline
scp -i $SSHKey $tempScript "${SSHUser}@${SSHHost}:/tmp/restart-service.sh"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "chmod +x /tmp/restart-service.sh && bash /tmp/restart-service.sh"
Remove-Item $tempScript

Write-Host "`nDeployment completed!" -ForegroundColor Green
Write-Host "`nProduction URLs:" -ForegroundColor Yellow
Write-Host "  API Base: http://${SSHHost}/api/v1" -ForegroundColor Cyan
Write-Host "  Health Check: http://${SSHHost}/health" -ForegroundColor Cyan
Write-Host "  API Docs: http://${SSHHost}/docs" -ForegroundColor Cyan
Write-Host "  ReDoc: http://${SSHHost}/redoc" -ForegroundColor Cyan

