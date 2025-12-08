# PowerShell script to setup HTTPS for Plant Delivery API
# Run this on the EC2 server via SSH

Write-Host "=== Setting up HTTPS for Plant Delivery API ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "1. Install Certbot (if not installed)"
Write-Host "2. Set up SSL certificate (Let's Encrypt or self-signed)"
Write-Host "3. Configure Nginx for HTTPS"
Write-Host ""

$hasDomain = Read-Host "Do you have a domain name pointing to this server? (y/n)"

if ($hasDomain -ne "y" -and $hasDomain -ne "Y") {
    Write-Host ""
    Write-Host "=== Alternative: Self-Signed Certificate ===" -ForegroundColor Yellow
    Write-Host "This will create a self-signed certificate for testing"
    Write-Host "Browsers will show a security warning but HTTPS will work"
    Write-Host ""
    $createSelfSigned = Read-Host "Create self-signed certificate? (y/n)"
    
    if ($createSelfSigned -eq "y" -or $createSelfSigned -eq "Y") {
        Write-Host "Creating self-signed certificate..." -ForegroundColor Green
        
        # Create SSL directory
        ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 "sudo mkdir -p /etc/nginx/ssl"
        
        # Generate self-signed certificate
        ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 @"
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/selfsigned.key \
    -out /etc/nginx/ssl/selfsigned.crt \
    -subj '/C=US/ST=State/L=City/O=Organization/CN=3.111.165.191'
"@
        
        Write-Host "Self-signed certificate created!" -ForegroundColor Green
        Write-Host "Note: Browsers will show a security warning" -ForegroundColor Yellow
    } else {
        Write-Host "Exiting. HTTPS setup requires either a domain name or self-signed certificate." -ForegroundColor Red
        exit 1
    }
} else {
    $domainName = Read-Host "Enter your domain name (e.g., api.yourdomain.com)"
    
    if ([string]::IsNullOrWhiteSpace($domainName)) {
        Write-Host "Domain name is required" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "Obtaining SSL certificate from Let's Encrypt..." -ForegroundColor Green
    
    # Install certbot if needed
    ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 "sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx"
    
    # Get certificate
    ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 "sudo certbot certonly --standalone -d $domainName --non-interactive --agree-tos --email admin@example.com"
    
    Write-Host "Certificate obtained successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Deploying HTTPS Configuration ===" -ForegroundColor Cyan

# Copy nginx-https.conf to server
scp -i C:\Users\ADMIN\.ssh\AWS.pem deploy\nginx-https.conf ubuntu@3.111.165.191:/tmp/nginx-https.conf

# Update nginx config on server
ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191 @"
sudo cp /tmp/nginx-https.conf /etc/nginx/sites-available/plant-delivery-api
sudo nginx -t
if [ `$? -eq 0 ]; then
    sudo systemctl reload nginx
    echo 'HTTPS configured successfully!'
else
    echo 'Nginx configuration test failed!'
    exit 1
fi
"@

Write-Host ""
Write-Host "=== HTTPS Setup Complete! ===" -ForegroundColor Green
Write-Host ""
if ($hasDomain -eq "y" -or $hasDomain -eq "Y") {
    Write-Host "Your API is now available at:" -ForegroundColor Cyan
    Write-Host "  - https://$domainName/api/v1" -ForegroundColor White
    Write-Host "  - https://$domainName/docs" -ForegroundColor White
    Write-Host "  - https://$domainName/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Update your admin panel to use: https://$domainName/api/v1" -ForegroundColor Yellow
} else {
    Write-Host "Your API is now available at:" -ForegroundColor Cyan
    Write-Host "  - https://3.111.165.191/api/v1" -ForegroundColor White
    Write-Host "  - https://3.111.165.191/docs" -ForegroundColor White
    Write-Host "  - https://3.111.165.191/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Browsers will show a security warning for self-signed certificates" -ForegroundColor Yellow
    Write-Host "Update your admin panel to use: https://3.111.165.191/api/v1" -ForegroundColor Yellow
}

