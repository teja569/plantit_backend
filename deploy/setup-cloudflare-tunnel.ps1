# Setup Cloudflare Tunnel for HTTPS (No domain required!)
# This creates a secure tunnel with valid SSL certificate

param(
    [string]$SSHKey = "$env:USERPROFILE\.ssh\AWS.pem",
    [string]$SSHUser = "ubuntu",
    [string]$SSHHost = "3.111.165.191"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Setting up Cloudflare Tunnel ===" -ForegroundColor Cyan
Write-Host "Server: ${SSHUser}@${SSHHost}" -ForegroundColor Yellow
Write-Host ""
Write-Host "This will create a secure HTTPS tunnel with valid SSL certificate" -ForegroundColor Green
Write-Host "No domain name required!" -ForegroundColor Green
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSHKey)) {
    Write-Host "Error: SSH key not found at $SSHKey" -ForegroundColor Red
    exit 1
}

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Green
$testResult = ssh -i $SSHKey -o StrictHostKeyChecking=no "${SSHUser}@${SSHHost}" "echo Connected" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot connect to server" -ForegroundColor Red
    Write-Host $testResult
    exit 1
}
Write-Host "✓ Connection successful" -ForegroundColor Green
Write-Host ""

# Step 1: Install cloudflared
Write-Host "Step 1: Installing cloudflared..." -ForegroundColor Cyan
$installCmd = @"
cd /tmp
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
cloudflared --version
"@
$installResult = ssh -i $SSHKey "${SSHUser}@${SSHHost}" $installCmd 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install cloudflared" -ForegroundColor Red
    Write-Host $installResult
    exit 1
}
Write-Host "✓ cloudflared installed" -ForegroundColor Green
Write-Host ""

# Step 2: Create systemd service for tunnel
Write-Host "Step 2: Creating tunnel service..." -ForegroundColor Cyan
$serviceContent = @"
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"@

# Create service file
$serviceFile = [System.IO.Path]::GetTempFileName()
$serviceContent | Out-File -FilePath $serviceFile -Encoding utf8
scp -i $SSHKey $serviceFile "${SSHUser}@${SSHHost}:/tmp/cloudflared-tunnel.service" | Out-Null
Remove-Item $serviceFile

# Install service
$serviceCmd = @"
sudo mv /tmp/cloudflared-tunnel.service /etc/systemd/system/cloudflared-tunnel.service
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-tunnel
echo 'Service created'
"@
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $serviceCmd | Out-Null
Write-Host "✓ Service created" -ForegroundColor Green
Write-Host ""

# Step 3: Start tunnel
Write-Host "Step 3: Starting tunnel..." -ForegroundColor Cyan
Write-Host "This will generate a URL like: https://random-name.trycloudflare.com" -ForegroundColor Yellow
Write-Host ""

# Start tunnel in background to get URL
$tunnelCmd = "sudo systemctl start cloudflared-tunnel && sleep 3 && sudo journalctl -u cloudflared-tunnel -n 20 --no-pager | grep -i 'trycloudflare.com' | head -1"
$tunnelUrl = ssh -i $SSHKey "${SSHUser}@${SSHHost}" $tunnelCmd 2>&1

# Check if tunnel is running
Start-Sleep -Seconds 5
$status = ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl is-active cloudflared-tunnel" 2>&1

if ($status -eq "active") {
    Write-Host "✓ Tunnel is running" -ForegroundColor Green
    Write-Host ""
    
    # Get the URL from logs
    $urlCmd = "sudo journalctl -u cloudflared-tunnel -n 50 --no-pager | grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' | head -1"
    $tunnelUrl = ssh -i $SSHKey "${SSHUser}@${SSHHost}" $urlCmd 2>&1
    
    if ($tunnelUrl -match "trycloudflare.com") {
        Write-Host "=== Cloudflare Tunnel Setup Complete! ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your API is now available at:" -ForegroundColor Cyan
        Write-Host "  - $tunnelUrl/api/v1" -ForegroundColor White
        Write-Host "  - $tunnelUrl/docs" -ForegroundColor White
        Write-Host "  - $tunnelUrl/health" -ForegroundColor White
        Write-Host ""
        Write-Host "⚠ Important:" -ForegroundColor Yellow
        Write-Host "  1. Update your admin panel to use: $tunnelUrl/api/v1" -ForegroundColor Yellow
        Write-Host "  2. This URL has a valid SSL certificate!" -ForegroundColor Green
        Write-Host "  3. The tunnel will auto-restart if it goes down" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To check tunnel status:" -ForegroundColor Cyan
        Write-Host "  ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 'sudo systemctl status cloudflared-tunnel'" -ForegroundColor White
        Write-Host ""
        Write-Host "To view tunnel URL:" -ForegroundColor Cyan
        Write-Host "  ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 'sudo journalctl -u cloudflared-tunnel -n 50 | grep trycloudflare.com'" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "⚠ Tunnel is running but URL not found in logs" -ForegroundColor Yellow
        Write-Host "Check logs manually:" -ForegroundColor Cyan
        Write-Host "  ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 'sudo journalctl -u cloudflared-tunnel -f'" -ForegroundColor White
    }
} else {
    Write-Host "Error: Tunnel failed to start" -ForegroundColor Red
    Write-Host "Check logs:" -ForegroundColor Yellow
    Write-Host "  ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 'sudo journalctl -u cloudflared-tunnel -n 50'" -ForegroundColor White
    exit 1
}

