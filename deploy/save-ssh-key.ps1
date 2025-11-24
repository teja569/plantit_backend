# Script to save SSH key and deploy
param(
    [string]$KeyContent = "",
    [string]$KeyPath = "$env:USERPROFILE\.ssh\AWS.pem"
)

Write-Host "Setting up SSH key for deployment..." -ForegroundColor Green

# Create .ssh directory if it doesn't exist
$sshDir = Split-Path $KeyPath -Parent
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Host "Created .ssh directory: $sshDir" -ForegroundColor Yellow
}

# If key content provided, save it
if ($KeyContent) {
    $KeyContent | Out-File -FilePath $KeyPath -Encoding ASCII -NoNewline
    Write-Host "SSH key saved to: $KeyPath" -ForegroundColor Green
}

# Set permissions (Windows)
try {
    icacls $KeyPath /inheritance:r 2>$null
    icacls $KeyPath /grant:r "$env:USERNAME:(R)" 2>$null
    Write-Host "SSH key permissions set" -ForegroundColor Green
} catch {
    Write-Host "Note: Could not set key permissions (may need admin)" -ForegroundColor Yellow
}

# Test connection
Write-Host "`nTesting SSH connection..." -ForegroundColor Green
$testResult = ssh -i $KeyPath -o StrictHostKeyChecking=no ubuntu@3.111.165.191 "echo 'Connection successful'" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "SSH connection successful!" -ForegroundColor Green
    Write-Host "`nYou can now deploy using:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File deploy/ec2-deploy.ps1" -ForegroundColor Cyan
} else {
    Write-Host "SSH connection failed. Please check:" -ForegroundColor Red
    Write-Host "  1. Key file exists and is correct" -ForegroundColor Yellow
    Write-Host "  2. Server is accessible" -ForegroundColor Yellow
    Write-Host "  3. Security group allows SSH (port 22)" -ForegroundColor Yellow
}

