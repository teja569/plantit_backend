#!/bin/bash

# Setup HTTPS for Plant Delivery API using Let's Encrypt
# This script sets up SSL/TLS certificates for the API server

set -e

echo "=== Setting up HTTPS for Plant Delivery API ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
else
    echo "Certbot is already installed"
fi

echo ""
echo "=== Important Notes ==="
echo "1. You need a domain name pointing to this server (3.111.165.191)"
echo "2. The domain must resolve to this IP address"
echo "3. Ports 80 and 443 must be open in your firewall"
echo ""

read -p "Do you have a domain name pointing to this server? (y/n): " has_domain

if [ "$has_domain" != "y" ] && [ "$has_domain" != "Y" ]; then
    echo ""
    echo "=== Alternative: Self-Signed Certificate (for testing) ==="
    echo "This will create a self-signed certificate that browsers will warn about"
    echo "but will allow HTTPS connections."
    echo ""
    read -p "Create self-signed certificate? (y/n): " create_self_signed
    
    if [ "$create_self_signed" == "y" ] || [ "$create_self_signed" == "Y" ]; then
        echo "Creating self-signed certificate..."
        
        # Create directory for certificates
        mkdir -p /etc/nginx/ssl
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/selfsigned.key \
            -out /etc/nginx/ssl/selfsigned.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=3.111.165.191"
        
        # Update nginx config for self-signed cert
        sed -i 's|ssl_certificate /etc/letsencrypt/live/3.111.165.191/fullchain.pem;|ssl_certificate /etc/nginx/ssl/selfsigned.crt;|' deploy/nginx-https.conf
        sed -i 's|ssl_certificate_key /etc/letsencrypt/live/3.111.165.191/privkey.pem;|ssl_certificate_key /etc/nginx/ssl/selfsigned.key;|' deploy/nginx-https.conf
        
        echo "Self-signed certificate created!"
        echo "Note: Browsers will show a security warning for self-signed certificates"
    else
        echo "Exiting. HTTPS setup requires either a domain name or self-signed certificate."
        exit 1
    fi
else
    read -p "Enter your domain name (e.g., api.yourdomain.com): " domain_name
    
    if [ -z "$domain_name" ]; then
        echo "Domain name is required"
        exit 1
    fi
    
    echo ""
    echo "Obtaining SSL certificate from Let's Encrypt..."
    echo "This will temporarily modify nginx configuration..."
    
    # Backup current nginx config
    cp /etc/nginx/sites-available/plant-delivery-api /etc/nginx/sites-available/plant-delivery-api.backup
    
    # Use certbot to get certificate
    certbot certonly --standalone -d "$domain_name" --non-interactive --agree-tos --email admin@example.com
    
    # Update nginx config with domain name
    sed -i "s|server_name 3.111.165.191 _;|server_name $domain_name 3.111.165.191 _;|g" deploy/nginx-https.conf
    sed -i "s|/etc/letsencrypt/live/3.111.165.191|/etc/letsencrypt/live/$domain_name|g" deploy/nginx-https.conf
    
    echo "Certificate obtained successfully!"
fi

echo ""
echo "=== Updating Nginx Configuration ==="

# Copy new nginx config
cp deploy/nginx-https.conf /etc/nginx/sites-available/plant-delivery-api

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Configuration is valid!"
    echo ""
    echo "Reloading nginx..."
    systemctl reload nginx
    echo ""
    echo "=== HTTPS Setup Complete! ==="
    echo ""
    if [ "$has_domain" == "y" ] || [ "$has_domain" == "Y" ]; then
        echo "Your API is now available at:"
        echo "  - https://$domain_name/api/v1"
        echo "  - https://$domain_name/docs"
        echo "  - https://$domain_name/health"
        echo ""
        echo "Update your admin panel to use: https://$domain_name/api/v1"
    else
        echo "Your API is now available at:"
        echo "  - https://3.111.165.191/api/v1"
        echo "  - https://3.111.165.191/docs"
        echo "  - https://3.111.165.191/health"
        echo ""
        echo "Note: Browsers will show a security warning for self-signed certificates"
        echo "Update your admin panel to use: https://3.111.165.191/api/v1"
    fi
else
    echo "Nginx configuration test failed!"
    echo "Restoring backup..."
    cp /etc/nginx/sites-available/plant-delivery-api.backup /etc/nginx/sites-available/plant-delivery-api
    exit 1
fi

