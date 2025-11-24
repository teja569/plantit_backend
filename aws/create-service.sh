#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

AWS_REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME=${CLUSTER_NAME:-plant-delivery-api-cluster}
SERVICE_NAME=${SERVICE_NAME:-plant-delivery-api-service}
TASK_DEFINITION=${TASK_DEFINITION:-plant-delivery-api}

echo -e "${GREEN}Creating ECS Service...${NC}"

# Get VPC and subnet IDs from Terraform output (if available)
# Or set them manually
VPC_ID=${VPC_ID:-""}
SUBNET_IDS=${SUBNET_IDS:-""}
SECURITY_GROUP_ID=${SECURITY_GROUP_ID:-""}
TARGET_GROUP_ARN=${TARGET_GROUP_ARN:-""}

if [ -z "$VPC_ID" ] || [ -z "$SUBNET_IDS" ] || [ -z "$SECURITY_GROUP_ID" ] || [ -z "$TARGET_GROUP_ARN" ]; then
    echo -e "${YELLOW}Please set the following environment variables:${NC}"
    echo "  VPC_ID"
    echo "  SUBNET_IDS (comma-separated)"
    echo "  SECURITY_GROUP_ID"
    echo "  TARGET_GROUP_ARN"
    echo ""
    echo "Or get them from Terraform outputs:"
    echo "  terraform output -json"
    exit 1
fi

# Convert comma-separated subnets to JSON array
SUBNET_ARRAY=$(echo $SUBNET_IDS | tr ',' '\n' | sed 's/^/      "/' | sed 's/$/",/' | tr '\n' ' ' | sed 's/,$//' | sed 's/^/[\n/' | sed 's/$/\n    ]/')

# Create service
aws ecs create-service \
  --cluster ${CLUSTER_NAME} \
  --service-name ${SERVICE_NAME} \
  --task-definition ${TASK_DEFINITION} \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS}],securityGroups=[${SECURITY_GROUP_ID}],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=${TARGET_GROUP_ARN},containerName=plant-delivery-api,containerPort=8000" \
  --health-check-grace-period-seconds 60 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100" \
  --enable-execute-command \
  --region ${AWS_REGION}

echo -e "${GREEN}ECS Service created successfully!${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"
echo -e "${YELLOW}Cluster: ${CLUSTER_NAME}${NC}"

