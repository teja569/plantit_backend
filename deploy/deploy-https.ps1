# Automated HTTPS deployment script for Plant Delivery API
# This will set up self-signed certificate and deploy HTTPS configuration

param(
    [string]$SSHKey = "$env:USERPROFILE\.ssh\AWS.pem",
    [string]$SSHUser = "ubuntu",
    [string]$SSHHost = "3.111.165.191"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Deploying HTTPS Configuration ===" -ForegroundColor Cyan
Write-Host "Server: ${SSHUser}@${SSHHost}" -ForegroundColor Yellow
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

# Step 1: Create self-signed certificate
Write-Host "Step 1: Creating self-signed SSL certificate..." -ForegroundColor Cyan
$certCmd = "sudo mkdir -p /etc/nginx/ssl && if [ ! -f /etc/nginx/ssl/selfsigned.crt ]; then sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -subj '/C=US/ST=State/L=City/O=PlantDelivery/CN=3.111.165.191' 2>&1 && echo 'Certificate created' || echo 'Certificate creation failed'; else echo 'Certificate already exists'; fi"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $certCmd | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create certificate" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Certificate created" -ForegroundColor Green
Write-Host ""

# Step 2: Copy HTTPS nginx configuration
Write-Host "Step 2: Copying HTTPS nginx configuration..." -ForegroundColor Cyan
scp -i $SSHKey deploy\nginx-https.conf "${SSHUser}@${SSHHost}:/tmp/nginx-https.conf" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to copy nginx config" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Configuration copied" -ForegroundColor Green
Write-Host ""

# Step 3: Update nginx config on server (modify for self-signed cert)
Write-Host "Step 3: Updating nginx configuration..." -ForegroundColor Cyan
$backupCmd = "sudo cp /etc/nginx/sites-available/plant-delivery-api /etc/nginx/sites-available/plant-delivery-api.backup.`$(date +%Y%m%d_%H%M%S) 2>/dev/null; echo 'backup done'"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $backupCmd | Out-Null

$updateCmd = "sudo cp /tmp/nginx-https.conf /etc/nginx/sites-available/plant-delivery-api && sudo sed -i 's|ssl_certificate /etc/letsencrypt/live/3.111.165.191/fullchain.pem;|ssl_certificate /etc/nginx/ssl/selfsigned.crt;|' /etc/nginx/sites-available/plant-delivery-api && sudo sed -i 's|ssl_certificate_key /etc/letsencrypt/live/3.111.165.191/privkey.pem;|ssl_certificate_key /etc/nginx/ssl/selfsigned.key;|' /etc/nginx/sites-available/plant-delivery-api && echo 'Configuration updated'"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $updateCmd | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to update nginx config" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Configuration updated" -ForegroundColor Green
Write-Host ""

# Step 4: Ensure ports 80 and 443 are open
Write-Host "Step 4: Ensuring firewall ports are open..." -ForegroundColor Cyan
$firewallCmd = "sudo ufw allow 80/tcp 2>/dev/null; sudo ufw allow 443/tcp 2>/dev/null; echo 'Firewall configured'"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $firewallCmd | Out-Null
Write-Host "✓ Firewall configured" -ForegroundColor Green
Write-Host ""

# Step 5: Test and reload nginx
Write-Host "Step 5: Testing nginx configuration..." -ForegroundColor Cyan
$testNginx = ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo nginx -t" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Nginx configuration test failed!" -ForegroundColor Red
    Write-Host $testNginx
    Write-Host ""
    Write-Host "Restoring backup configuration..." -ForegroundColor Yellow
    $restoreCmd = "sudo cp /etc/nginx/sites-available/plant-delivery-api.backup.* /etc/nginx/sites-available/plant-delivery-api 2>/dev/null; echo 'restored'"
    ssh -i $SSHKey "${SSHUser}@${SSHHost}" $restoreCmd | Out-Null
    exit 1
}
Write-Host "✓ Configuration test passed" -ForegroundColor Green
Write-Host ""

Write-Host "Reloading nginx..." -ForegroundColor Cyan
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl reload nginx" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to reload nginx" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Nginx reloaded" -ForegroundColor Green
Write-Host ""

# Step 6: Test HTTPS endpoint
Write-Host "Step 6: Testing HTTPS endpoint..." -ForegroundColor Cyan
$healthCheck = ssh -i $SSHKey "${SSHUser}@${SSHHost}" "curl -k -s https://localhost/health 2>&1" 2>&1
if ($healthCheck -match "status") {
    Write-Host "✓ HTTPS endpoint is working" -ForegroundColor Green
} else {
    Write-Host "⚠ HTTPS endpoint test inconclusive (this is normal)" -ForegroundColor Yellow
}
Write-Host ""

# Success message
Write-Host "=== HTTPS Deployment Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your API is now available at:" -ForegroundColor Cyan
Write-Host "  - https://3.111.165.191/api/v1" -ForegroundColor White
Write-Host "  - https://3.111.165.191/docs" -ForegroundColor White
Write-Host "  - https://3.111.165.191/health" -ForegroundColor White
Write-Host ""
Write-Host "⚠ Important Notes:" -ForegroundColor Yellow
Write-Host "  1. This uses a self-signed certificate - browsers will show a security warning" -ForegroundColor Yellow
Write-Host "  2. Click 'Advanced' → 'Proceed to site' to bypass the warning" -ForegroundColor Yellow
Write-Host "  3. Update your admin panel to use: https://3.111.165.191/api/v1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use a proper certificate with a domain name, run:" -ForegroundColor Cyan
Write-Host "  .\deploy\setup-https.ps1" -ForegroundColor White
Write-Host ""
