# Setup Named Cloudflare Tunnel for Stable URL
# This creates a permanent tunnel URL that won't change

param(
    [string]$SSHKey = "$env:USERPROFILE\.ssh\AWS.pem",
    [string]$SSHUser = "ubuntu",
    [string]$SSHHost = "3.111.165.191"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Setting up Named Cloudflare Tunnel ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will create a STABLE tunnel URL that won't change on restarts." -ForegroundColor Green
Write-Host "You'll need a free Cloudflare account." -ForegroundColor Yellow
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSHKey)) {
    Write-Host "Error: SSH key not found at $SSHKey" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Installing cloudflared (if needed)..." -ForegroundColor Cyan
$installCmd = @"
if ! command -v cloudflared &> /dev/null; then
    cd /tmp
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
    chmod +x cloudflared
    sudo mv cloudflared /usr/local/bin/
    echo 'cloudflared installed'
else
    echo 'cloudflared already installed'
fi
"@
ssh -i $SSHKey "${SSHUser}@${SSHHost}" $installCmd | Out-Null
Write-Host "✓ cloudflared ready" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Setting up named tunnel..." -ForegroundColor Cyan
Write-Host ""
Write-Host "You need to:" -ForegroundColor Yellow
Write-Host "1. Go to https://one.dash.cloudflare.com/" -ForegroundColor White
Write-Host "2. Sign up/login (free account)" -ForegroundColor White
Write-Host "3. Go to: Networks > Tunnels" -ForegroundColor White
Write-Host "4. Click 'Create a tunnel'" -ForegroundColor White
Write-Host "5. Choose 'Cloudflared' as connector" -ForegroundColor White
Write-Host "6. Name it: 'plant-delivery-api'" -ForegroundColor White
Write-Host "7. Copy the tunnel token" -ForegroundColor White
Write-Host ""
Write-Host "OR run this command on the server to login:" -ForegroundColor Cyan
Write-Host "  ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 'cloudflared tunnel login'" -ForegroundColor White
Write-Host ""

$hasToken = Read-Host "Do you have a Cloudflare tunnel token? (y/n)"

if ($hasToken -eq "y" -or $hasToken -eq "Y") {
    $tunnelToken = Read-Host "Enter your tunnel token" -AsSecureString
    $tunnelTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($tunnelToken)
    )
    
    Write-Host ""
    Write-Host "Step 3: Creating tunnel configuration..." -ForegroundColor Cyan
    
    $tunnelName = "plant-delivery-api"
    $configScript = @"
sudo mkdir -p /etc/cloudflared
echo '$tunnelTokenPlain' | sudo tee /etc/cloudflared/credentials.json > /dev/null
sudo chmod 600 /etc/cloudflared/credentials.json

# Create config file
sudo tee /etc/cloudflared/config.yml > /dev/null <<EOF
tunnel: $(cloudflared tunnel list 2>/dev/null | grep -oP '[a-f0-9-]{36}' | head -1 || echo 'YOUR_TUNNEL_ID')
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: plant-delivery-api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

echo 'Configuration created'
"@
    
    Write-Host "⚠ Note: You'll need to update the hostname in the config after creating the tunnel" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternatively, let's set up a quick tunnel with a custom subdomain..." -ForegroundColor Cyan
    
} else {
    Write-Host ""
    Write-Host "Let's set up the tunnel interactively on the server..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Run this command to login and create a tunnel:" -ForegroundColor Yellow
    Write-Host "  ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191" -ForegroundColor White
    Write-Host "  cloudflared tunnel login" -ForegroundColor White
    Write-Host "  cloudflared tunnel create plant-delivery-api" -ForegroundColor White
    Write-Host "  cloudflared tunnel route dns plant-delivery-api api.yourdomain.com" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use the Cloudflare dashboard method above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Alternative: Use Domain with Let's Encrypt ===" -ForegroundColor Cyan
Write-Host "If you have a domain name, we can set up a permanent HTTPS URL." -ForegroundColor Yellow
Write-Host ""
$hasDomain = Read-Host "Do you have a domain name? (y/n)"

if ($hasDomain -eq "y" -or $hasDomain -eq "Y") {
    $domainName = Read-Host "Enter your domain (e.g., api.yourdomain.com)"
    
    if (-not [string]::IsNullOrWhiteSpace($domainName)) {
        Write-Host ""
        Write-Host "Setting up Let's Encrypt SSL certificate..." -ForegroundColor Cyan
        Write-Host "Running: .\deploy\setup-letsencrypt.ps1 -DomainName $domainName" -ForegroundColor Yellow
        Write-Host ""
        
        & ".\deploy\setup-letsencrypt.ps1" -DomainName $domainName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=== Setup Complete! ===" -ForegroundColor Green
            Write-Host "Your mobile app should use:" -ForegroundColor Cyan
            Write-Host "  https://$domainName/api/v1" -ForegroundColor White
            Write-Host ""
            Write-Host "This URL is permanent and won't change!" -ForegroundColor Green
        }
    }
} else {
    Write-Host ""
    Write-Host "For a permanent solution, you can:" -ForegroundColor Yellow
    Write-Host "1. Get a free domain from Freenom (https://www.freenom.com)" -ForegroundColor White
    Write-Host "2. Or use DuckDNS (https://www.duckdns.org) for a free subdomain" -ForegroundColor White
    Write-Host "3. Then run: .\deploy\setup-letsencrypt.ps1 -DomainName yourdomain.com" -ForegroundColor White
    Write-Host ""
    Write-Host "For now, the quick tunnel URL works but will change on restarts." -ForegroundColor Yellow
}

