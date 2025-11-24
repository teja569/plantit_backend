#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPO=${ECR_REPO:-plant-delivery-api}
ECS_CLUSTER=${ECS_CLUSTER:-plant-delivery-api-cluster}
ECS_SERVICE=${ECS_SERVICE:-plant-delivery-api-service}
IMAGE_TAG=${IMAGE_TAG:-latest}

echo -e "${GREEN}Starting AWS deployment...${NC}"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"

echo -e "${YELLOW}AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"
echo -e "${YELLOW}ECR URI: ${ECR_URI}${NC}"

# Step 1: Login to ECR
echo -e "${GREEN}Step 1: Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

# Step 2: Build Docker image
echo -e "${GREEN}Step 2: Building Docker image...${NC}"
docker build -t ${ECR_REPO}:${IMAGE_TAG} .
docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

# Step 3: Push to ECR
echo -e "${GREEN}Step 3: Pushing image to ECR...${NC}"
docker push ${ECR_URI}:${IMAGE_TAG}

# Step 4: Update ECS service
echo -e "${GREEN}Step 4: Updating ECS service...${NC}"
aws ecs update-service \
  --cluster ${ECS_CLUSTER} \
  --service ${ECS_SERVICE} \
  --force-new-deployment \
  --region ${AWS_REGION} > /dev/null

echo -e "${GREEN}Deployment initiated!${NC}"
echo -e "${YELLOW}Waiting for service to stabilize...${NC}"

# Wait for service to be stable
aws ecs wait services-stable \
  --cluster ${ECS_CLUSTER} \
  --services ${ECS_SERVICE} \
  --region ${AWS_REGION}

echo -e "${GREEN}Deployment completed successfully!${NC}"

# Get service status
echo -e "${GREEN}Service Status:${NC}"
aws ecs describe-services \
  --cluster ${ECS_CLUSTER} \
  --services ${ECS_SERVICE} \
  --region ${AWS_REGION} \
  --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}' \
  --output table

