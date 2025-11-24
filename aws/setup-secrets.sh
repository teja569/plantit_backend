#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

AWS_REGION=${AWS_REGION:-us-east-1}
SECRET_PREFIX="plant-delivery-api"

echo -e "${GREEN}Setting up AWS Secrets Manager secrets...${NC}"

# Function to create or update secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    local full_name="${SECRET_PREFIX}/${secret_name}"
    
    echo -e "${YELLOW}Creating/updating secret: ${full_name}${NC}"
    
    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id "${full_name}" --region ${AWS_REGION} > /dev/null 2>&1; then
        echo -e "${YELLOW}Secret exists, updating...${NC}"
        aws secretsmanager update-secret \
            --secret-id "${full_name}" \
            --secret-string "${secret_value}" \
            --region ${AWS_REGION} > /dev/null
    else
        echo -e "${YELLOW}Creating new secret...${NC}"
        aws secretsmanager create-secret \
            --name "${full_name}" \
            --secret-string "${secret_value}" \
            --region ${AWS_REGION} > /dev/null
    fi
    
    echo -e "${GREEN}✓ Secret ${full_name} ready${NC}"
}

# Database URL
read -sp "Enter DATABASE_URL (postgresql://user:pass@host:port/db): " DB_URL
echo
create_secret "database-url" "${DB_URL}"

# Secret Key
read -sp "Enter SECRET_KEY (for JWT): " SECRET_KEY
echo
create_secret "secret-key" "${SECRET_KEY}"

# Gemini API Key
read -sp "Enter GEMINI_API_KEY: " GEMINI_KEY
echo
create_secret "gemini-api-key" "${GEMINI_KEY}"

# AWS Access Key ID
read -sp "Enter AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY
echo
create_secret "aws-access-key" "${AWS_ACCESS_KEY}"

# AWS Secret Access Key
read -sp "Enter AWS_SECRET_ACCESS_KEY: " AWS_SECRET_KEY
echo
create_secret "aws-secret-key" "${AWS_SECRET_KEY}"

# Optional: Cloudinary credentials
read -p "Do you want to set Cloudinary credentials? (y/n): " SET_CLOUDINARY
if [ "$SET_CLOUDINARY" = "y" ]; then
    read -p "Enter CLOUDINARY_CLOUD_NAME: " CLOUD_NAME
    read -p "Enter CLOUDINARY_API_KEY: " CLOUD_KEY
    read -sp "Enter CLOUDINARY_API_SECRET: " CLOUD_SECRET
    echo
    
    create_secret "cloudinary-cloud-name" "${CLOUD_NAME}"
    create_secret "cloudinary-api-key" "${CLOUD_KEY}"
    create_secret "cloudinary-api-secret" "${CLOUD_SECRET}"
fi

# Optional: SendGrid API Key
read -p "Do you want to set SendGrid API key? (y/n): " SET_SENDGRID
if [ "$SET_SENDGRID" = "y" ]; then
    read -sp "Enter SENDGRID_API_KEY: " SENDGRID_KEY
    echo
    create_secret "sendgrid-api-key" "${SENDGRID_KEY}"
fi

echo -e "${GREEN}All secrets have been set up!${NC}"
echo -e "${YELLOW}Note: Update your ECS task definition to reference these secrets.${NC}"

