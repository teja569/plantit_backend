#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SSH_KEY="${SSH_KEY:-~/.ssh/AWS.pem}"
SSH_USER="${SSH_USER:-ubuntu}"
SSH_HOST="${SSH_HOST:-3.111.165.191}"

echo -e "${GREEN}Setting up EC2 server for Plant Delivery API...${NC}"

# Check if SSH key exists
if [ ! -f "${SSH_KEY/#\~/$HOME}" ]; then
    echo -e "${RED}Error: SSH key not found at ${SSH_KEY}${NC}"
    exit 1
fi

# Setup server
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'ENDSSH'
set -e

echo "Updating system packages..."
sudo apt-get update -y

echo "Installing Python 3.11 and dependencies..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt-get install -y postgresql-client libpq-dev build-essential
sudo apt-get install -y nginx supervisor curl git

echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "Creating application directory..."
sudo mkdir -p /opt/plant-delivery-api
sudo mkdir -p /opt/plant-delivery-api/logs
sudo mkdir -p /opt/plant-delivery-api/models
sudo chown -R ubuntu:ubuntu /opt/plant-delivery-api

echo "Setting up firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "Server setup completed!"
ENDSSH

echo -e "${GREEN}Server setup completed successfully!${NC}"
echo -e "${YELLOW}You can now deploy the application using deploy/ec2-deploy.sh${NC}"

