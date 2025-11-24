#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/AWS.pem}"
SSH_USER="${SSH_USER:-ubuntu}"
SSH_HOST="${SSH_HOST:-3.111.165.191}"
APP_NAME="plant-delivery-api"
REMOTE_DIR="/opt/${APP_NAME}"
SERVICE_NAME="${APP_NAME}"

echo -e "${GREEN}Starting EC2 deployment...${NC}"
echo -e "${YELLOW}Server: ${SSH_USER}@${SSH_HOST}${NC}"

# Check if SSH key exists
if [ ! -f "${SSH_KEY/#\~/$HOME}" ]; then
    echo -e "${RED}Error: SSH key not found at ${SSH_KEY}${NC}"
    exit 1
fi

# Test SSH connection
echo -e "${GREEN}Testing SSH connection...${NC}"
ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=no "${SSH_USER}@${SSH_HOST}" "echo 'Connection successful'" || {
    echo -e "${RED}Error: Cannot connect to server${NC}"
    exit 1
}

# Create remote directory structure
echo -e "${GREEN}Setting up remote directory structure...${NC}"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'ENDSSH'
sudo mkdir -p /opt/plant-delivery-api
sudo mkdir -p /opt/plant-delivery-api/logs
sudo mkdir -p /opt/plant-delivery-api/models
sudo chown -R ubuntu:ubuntu /opt/plant-delivery-api
ENDSSH

# Install dependencies on remote server
echo -e "${GREEN}Installing dependencies on server...${NC}"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'ENDSSH'
# Update system
sudo apt-get update -y

# Install Python and dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip python3-dev
sudo apt-get install -y postgresql-client libpq-dev build-essential
sudo apt-get install -y nginx supervisor curl

# Install Node.js for building (if needed)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
ENDSSH

# Create virtual environment and install dependencies
echo -e "${GREEN}Setting up Python virtual environment...${NC}"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << ENDSSH
cd ${REMOTE_DIR}
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
ENDSSH

# Copy application files
echo -e "${GREEN}Copying application files...${NC}"
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude '.git' --exclude '*.db' --exclude '*.log' \
    --exclude 'node_modules' --exclude '.env' \
    -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no" \
    ./ "${SSH_USER}@${SSH_HOST}:${REMOTE_DIR}/"

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << ENDSSH
cd ${REMOTE_DIR}
source venv/bin/activate
pip install -r requirements.txt
ENDSSH

# Copy systemd service file
echo -e "${GREEN}Setting up systemd service...${NC}"
scp -i "${SSH_KEY}" deploy/plant-delivery-api.service "${SSH_USER}@${SSH_HOST}:/tmp/"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'ENDSSH'
sudo mv /tmp/plant-delivery-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable plant-delivery-api
ENDSSH

# Copy nginx configuration
echo -e "${GREEN}Setting up Nginx...${NC}"
scp -i "${SSH_KEY}" deploy/nginx.conf "${SSH_USER}@${SSH_HOST}:/tmp/plant-delivery-api-nginx.conf"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'ENDSSH'
sudo mv /tmp/plant-delivery-api-nginx.conf /etc/nginx/sites-available/plant-delivery-api
sudo ln -sf /etc/nginx/sites-available/plant-delivery-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
ENDSSH

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << ENDSSH
cd ${REMOTE_DIR}
source venv/bin/activate
export \$(cat .env | xargs) 2>/dev/null || true
alembic upgrade head || echo "Migrations skipped or failed"
ENDSSH

# Restart service
echo -e "${GREEN}Restarting service...${NC}"
ssh -i "${SSH_KEY}" "${SSH_USER}@${SSH_HOST}" << 'ENDSSH'
sudo systemctl restart plant-delivery-api
sudo systemctl status plant-delivery-api --no-pager
ENDSSH

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${YELLOW}Application URL: http://${SSH_HOST}${NC}"
echo -e "${YELLOW}API URL: http://${SSH_HOST}/api/v1${NC}"
echo -e "${YELLOW}Health Check: http://${SSH_HOST}/health${NC}"

