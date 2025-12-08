# Setup DuckDNS for Free Permanent Domain
# This creates a stable URL like: https://yourname.duckdns.org

param(
    [string]$SSHKey = "$env:USERPROFILE\.ssh\AWS.pem",
    [string]$SSHUser = "ubuntu",
    [string]$SSHHost = "3.111.165.191"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Setting up DuckDNS Free Domain ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will give you a FREE permanent domain like: yourname.duckdns.org" -ForegroundColor Green
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSHKey)) {
    Write-Host "Error: SSH key not found at $SSHKey" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Get DuckDNS Token" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://www.duckdns.org" -ForegroundColor White
Write-Host "2. Sign in with Google/GitHub/Twitter (free)" -ForegroundColor White
Write-Host "3. Click 'domains' in the menu" -ForegroundColor White
Write-Host "4. Choose a subdomain name (e.g., 'plantapi')" -ForegroundColor White
Write-Host "5. Copy your token from the page" -ForegroundColor White
Write-Host ""

$duckdnsToken = Read-Host "Enter your DuckDNS token"
$duckdnsSubdomain = Read-Host "Enter your DuckDNS subdomain (e.g., 'plantapi' for plantapi.duckdns.org)"

if ([string]::IsNullOrWhiteSpace($duckdnsToken) -or [string]::IsNullOrWhiteSpace($duckdnsSubdomain)) {
    Write-Host "Error: Token and subdomain are required" -ForegroundColor Red
    exit 1
}

$duckdnsDomain = "$duckdnsSubdomain.duckdns.org"

Write-Host ""
Write-Host "Step 2: Updating DuckDNS DNS..." -ForegroundColor Cyan
Write-Host "Setting $duckdnsDomain to point to $SSHHost" -ForegroundColor Yellow

# Update DuckDNS
$updateUrl = "https://www.duckdns.org/update?domains=$duckdnsSubdomain&token=$duckdnsToken&ip=$SSHHost"
$updateResult = Invoke-WebRequest -Uri $updateUrl -UseBasicParsing

if ($updateResult.Content -eq "OK") {
    Write-Host "✓ DuckDNS updated successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ DuckDNS update response: $($updateResult.Content)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Waiting for DNS propagation..." -ForegroundColor Cyan
Write-Host "Waiting 30 seconds for DNS to propagate..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Step 4: Setting up Let's Encrypt SSL..." -ForegroundColor Cyan
Write-Host "Running Let's Encrypt setup for $duckdnsDomain" -ForegroundColor Yellow
Write-Host ""

# Run Let's Encrypt setup
& ".\deploy\setup-letsencrypt.ps1" -DomainName $duckdnsDomain -Email "admin@$duckdnsDomain"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Setup Complete! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your PERMANENT API URL:" -ForegroundColor Cyan
    Write-Host "  https://$duckdnsDomain/api/v1" -ForegroundColor White
    Write-Host ""
    Write-Host "Use this URL for:" -ForegroundColor Yellow
    Write-Host "  ✓ Mobile App" -ForegroundColor Green
    Write-Host "  ✓ Admin Panel" -ForegroundColor Green
    Write-Host "  ✓ Any other clients" -ForegroundColor Green
    Write-Host ""
    Write-Host "This URL will NEVER change!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: Update DuckDNS periodically (or set up auto-update)" -ForegroundColor Yellow
    Write-Host "  URL: https://www.duckdns.org/update?domains=$duckdnsSubdomain&token=$duckdnsToken&ip=$SSHHost" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "Let's Encrypt setup had issues. You can try manually:" -ForegroundColor Yellow
    Write-Host "  .\deploy\setup-letsencrypt.ps1 -DomainName $duckdnsDomain" -ForegroundColor White
}

