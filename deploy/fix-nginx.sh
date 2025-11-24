#!/bin/bash
# Fix Nginx port conflict and restart

echo "Checking what's using port 80..."
sudo lsof -i :80 || sudo netstat -tulpn | grep :80

echo "Stopping conflicting services..."
sudo systemctl stop apache2 2>/dev/null || true
sudo fuser -k 80/tcp 2>/dev/null || true

echo "Removing default Nginx config if conflicting..."
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Starting Nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

echo "Nginx status:"
sudo systemctl status nginx --no-pager | head -10

