# Setup Let's Encrypt SSL Certificate for Plant Delivery API
# This requires a domain name pointing to 3.111.165.191

param(
    [Parameter(Mandatory=$true)]
    [string]$DomainName,
    
    [string]$Email = "admin@example.com",
    [string]$SSHKey = "$env:USERPROFILE\.ssh\AWS.pem",
    [string]$SSHUser = "ubuntu",
    [string]$SSHHost = "3.111.165.191"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Setting up Let's Encrypt SSL Certificate ===" -ForegroundColor Cyan
Write-Host "Domain: $DomainName" -ForegroundColor Yellow
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

# Step 1: Install Certbot
Write-Host "Step 1: Installing Certbot..." -ForegroundColor Cyan
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo apt-get update -qq && sudo apt-get install -y certbot python3-certbot-nginx" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install Certbot" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Certbot installed" -ForegroundColor Green
Write-Host ""

# Step 2: Temporarily stop nginx for standalone mode
Write-Host "Step 2: Stopping nginx temporarily for certificate generation..." -ForegroundColor Cyan
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl stop nginx" | Out-Null
Write-Host "✓ Nginx stopped" -ForegroundColor Green
Write-Host ""

# Step 3: Obtain certificate
Write-Host "Step 3: Obtaining SSL certificate from Let's Encrypt..." -ForegroundColor Cyan
Write-Host "This may take a minute..." -ForegroundColor Yellow
$certResult = ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo certbot certonly --standalone -d $DomainName --non-interactive --agree-tos --email $Email --preferred-challenges http" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to obtain certificate" -ForegroundColor Red
    Write-Host $certResult
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Domain DNS must point to $SSHHost" -ForegroundColor Yellow
    Write-Host "  2. Port 80 must be accessible from the internet" -ForegroundColor Yellow
    Write-Host "  3. Wait a few minutes after DNS changes" -ForegroundColor Yellow
    
    # Restart nginx
    ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl start nginx" | Out-Null
    exit 1
}
Write-Host "✓ Certificate obtained successfully" -ForegroundColor Green
Write-Host ""

# Step 4: Update nginx configuration
Write-Host "Step 4: Updating nginx configuration..." -ForegroundColor Cyan
scp -i $SSHKey deploy\nginx-https.conf "${SSHUser}@${SSHHost}:/tmp/nginx-https.conf" | Out-Null

$updateScript = "sudo cp /tmp/nginx-https.conf /etc/nginx/sites-available/plant-delivery-api && sudo sed -i 's|server_name 3.111.165.191 _;|server_name $DomainName 3.111.165.191 _;|g' /etc/nginx/sites-available/plant-delivery-api && sudo sed -i 's|/etc/letsencrypt/live/3.111.165.191|/etc/letsencrypt/live/$DomainName|g' /etc/nginx/sites-available/plant-delivery-api && echo 'Configuration updated'"
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $updateScript | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to update nginx config" -ForegroundColor Red
    ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl start nginx" | Out-Null
    exit 1
}
Write-Host "✓ Configuration updated" -ForegroundColor Green
Write-Host ""

# Step 5: Test and start nginx
Write-Host "Step 5: Testing nginx configuration..." -ForegroundColor Cyan
$testNginx = ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo nginx -t" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Nginx configuration test failed!" -ForegroundColor Red
    Write-Host $testNginx
    ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl start nginx" | Out-Null
    exit 1
}
Write-Host "✓ Configuration test passed" -ForegroundColor Green
Write-Host ""

Write-Host "Starting nginx..." -ForegroundColor Cyan
ssh -i $SSHKey "${SSHUser}@${SSHHost}" "sudo systemctl start nginx" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start nginx" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Nginx started" -ForegroundColor Green
Write-Host ""

# Step 6: Test HTTPS endpoint
Write-Host "Step 6: Testing HTTPS endpoint..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
$healthCheck = ssh -i $SSHKey "${SSHUser}@${SSHHost}" "curl -s https://localhost/health" 2>&1
if ($healthCheck -match "status") {
    Write-Host "✓ HTTPS endpoint is working" -ForegroundColor Green
} else {
    Write-Host "⚠ HTTPS endpoint test inconclusive" -ForegroundColor Yellow
}
Write-Host ""

# Success message
Write-Host "=== SSL Certificate Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your API is now available at:" -ForegroundColor Cyan
Write-Host "  - https://$DomainName/api/v1" -ForegroundColor White
Write-Host "  - https://$DomainName/docs" -ForegroundColor White
Write-Host "  - https://$DomainName/health" -ForegroundColor White
Write-Host ""
Write-Host "⚠ Important:" -ForegroundColor Yellow
Write-Host "  1. Update your admin panel to use: https://$DomainName/api/v1" -ForegroundColor Yellow
Write-Host "  2. Certificate will auto-renew via certbot" -ForegroundColor Yellow
Write-Host "  3. Test certificate renewal: sudo certbot renew --dry-run" -ForegroundColor Yellow
Write-Host ""

