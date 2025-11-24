# AWS Deployment Guide

Complete guide for deploying Plant Delivery API to AWS.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Infrastructure Setup](#infrastructure-setup)
5. [Application Deployment](#application-deployment)
6. [Configuration](#configuration)
7. [Monitoring](#monitoring)
8. [Scaling](#scaling)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

## Architecture Overview

```
Internet
    ↓
Application Load Balancer (HTTPS)
    ↓
ECS Fargate (Multiple Tasks)
    ↓
RDS PostgreSQL (Multi-AZ)
    ↓
S3 (Static Files)
    ↓
CloudWatch (Logs & Metrics)
```

### Components

- **ECS Fargate**: Serverless container orchestration
- **RDS PostgreSQL**: Managed database with automated backups
- **Application Load Balancer**: Traffic distribution and SSL termination
- **S3**: Static file storage (images, uploads)
- **CloudWatch**: Logging and monitoring
- **Secrets Manager**: Secure credential storage
- **ECR**: Docker image registry
- **VPC**: Isolated network environment

## Prerequisites

1. **AWS Account** with admin access
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **Terraform** >= 1.0
   ```bash
   terraform version
   ```
4. **Docker** installed
5. **Domain name** (optional but recommended)
6. **SSL Certificate** in ACM (for HTTPS)

## Quick Start

### Step 1: Set Up Secrets

```bash
cd aws
chmod +x setup-secrets.sh
./setup-secrets.sh
```

This creates secrets in AWS Secrets Manager for:
- Database credentials
- JWT secret key
- API keys (Gemini, AWS, etc.)

### Step 2: Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Deploy
terraform plan
terraform apply
```

### Step 3: Build and Push Docker Image

```bash
# Get ECR repository URL from Terraform output
ECR_URI=$(terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URI

# Build and push
docker build -t plant-delivery-api:latest .
docker tag plant-delivery-api:latest $ECR_URI:latest
docker push $ECR_URI:latest
```

### Step 4: Create ECS Task Definition

Update `aws/ecs-task-definition.json` with your values, then:

```bash
aws ecs register-task-definition \
  --cli-input-json file://aws/ecs-task-definition.json
```

### Step 5: Create ECS Service

```bash
# Get values from Terraform outputs
export VPC_ID=$(terraform output -raw vpc_id)
export SUBNET_IDS=$(terraform output -json private_subnets | jq -r 'join(",")')
export SECURITY_GROUP_ID=$(terraform output -raw ecs_security_group_id)
export TARGET_GROUP_ARN=$(terraform output -raw target_group_arn)

# Create service
chmod +x aws/create-service.sh
./aws/create-service.sh
```

### Step 6: Run Database Migrations

```bash
aws ecs run-task \
  --cluster plant-delivery-api-cluster \
  --task-definition plant-delivery-api \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "plant-delivery-api",
      "command": ["alembic", "upgrade", "head"]
    }]
  }'
```

## Infrastructure Setup

### Terraform Configuration

The Terraform configuration creates:

1. **VPC** with public and private subnets
2. **RDS PostgreSQL** database
3. **ECS Cluster** for container orchestration
4. **Application Load Balancer** with HTTPS
5. **ECR Repository** for Docker images
6. **S3 Bucket** for static files
7. **Security Groups** for network security
8. **IAM Roles** for ECS tasks
9. **CloudWatch Log Groups** for logging

### Customization

Edit `aws/terraform/variables.tf` and `terraform.tfvars` to customize:
- Region
- Instance sizes
- Database configuration
- VPC CIDR blocks
- Resource names

## Application Deployment

### Manual Deployment

```bash
chmod +x aws/deploy.sh
./aws/deploy.sh
```

### Automated Deployment (GitHub Actions)

1. Set GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. Push to `main` branch to trigger deployment

### Update Application

```bash
# Build new image
docker build -t plant-delivery-api:latest .

# Tag and push
docker tag plant-delivery-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Force new deployment
aws ecs update-service \
  --cluster plant-delivery-api-cluster \
  --service plant-delivery-api-service \
  --force-new-deployment
```

## Configuration

### Environment Variables

The application reads from AWS Secrets Manager. Update secrets:

```bash
aws secretsmanager update-secret \
  --secret-id plant-delivery-api/database-url \
  --secret-string "postgresql://user:pass@host:5432/db"
```

### Database Connection

RDS automatically provides SSL. Use this format:

```
postgresql://username:password@rds-endpoint:5432/database?sslmode=require
```

### S3 Configuration

Update task definition to include S3 bucket name:

```json
{
  "environment": [
    {
      "name": "AWS_BUCKET_NAME",
      "value": "plant-delivery-api-static-production"
    }
  ]
}
```

### CORS Configuration

Set allowed origins in Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name plant-delivery-api/allowed-origins \
  --secret-string "https://yourdomain.com,https://www.yourdomain.com"
```

## Monitoring

### CloudWatch Logs

View logs:

```bash
aws logs tail /ecs/plant-delivery-api --follow
```

### CloudWatch Metrics

ECS automatically sends:
- CPU utilization
- Memory utilization
- Task count
- Service health

### Health Checks

The `/health` endpoint checks:
- Database connectivity
- Gemini API status
- System health

Access via ALB:
```bash
curl https://your-alb-dns-name/health
```

## Scaling

### Manual Scaling

```bash
aws ecs update-service \
  --cluster plant-delivery-api-cluster \
  --service plant-delivery-api-service \
  --desired-count 4
```

### Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/plant-delivery-api-cluster/plant-delivery-api-service \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/plant-delivery-api-cluster/plant-delivery-api-service \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

## Security

### SSL/TLS

1. Request certificate in ACM
2. Update ALB listener to use certificate
3. Configure HTTPS redirect

### Security Groups

- **ALB**: Allow HTTP/HTTPS from internet
- **ECS**: Allow port 8000 from ALB only
- **RDS**: Allow PostgreSQL from ECS only

### IAM Roles

- **ECS Execution Role**: Pull images, write logs, read secrets
- **ECS Task Role**: Access S3 and other AWS services

### Secrets Management

All sensitive data stored in AWS Secrets Manager:
- Database credentials
- API keys
- JWT secrets

## Troubleshooting

### Service Not Starting

```bash
# Check service events
aws ecs describe-services \
  --cluster plant-delivery-api-cluster \
  --services plant-delivery-api-service \
  --query 'services[0].events[:5]'

# Check task status
aws ecs list-tasks \
  --cluster plant-delivery-api-cluster \
  --service-name plant-delivery-api-service
```

### Database Connection Issues

```bash
# Verify security groups
aws ec2 describe-security-groups \
  --group-ids sg-xxx

# Test database connectivity from ECS task
aws ecs execute-command \
  --cluster plant-delivery-api-cluster \
  --task TASK_ID \
  --container plant-delivery-api \
  --command "psql $DATABASE_URL -c 'SELECT 1'"
```

### View Logs

```bash
# Real-time logs
aws logs tail /ecs/plant-delivery-api --follow

# Search logs
aws logs filter-log-events \
  --log-group-name /ecs/plant-delivery-api \
  --filter-pattern "ERROR"
```

### Health Check Failures

```bash
# Check health endpoint
curl https://your-alb-dns-name/health

# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...
```

## Cost Optimization

1. **Use Reserved Instances** for RDS (if predictable)
2. **Enable RDS Auto Scaling** for storage
3. **Set up S3 Lifecycle Policies** for old files
4. **Enable CloudWatch Logs Retention** (30 days)
5. **Use Spot Instances** for ECS (if fault-tolerant)

## Backup and Recovery

### RDS Backups

- Automated: 7 days retention
- Manual: Create snapshots before major changes

### Application Backups

- Database: RDS automated backups
- Static files: S3 versioning
- Configuration: Terraform state in S3

## Maintenance

### Update Application

```bash
./aws/deploy.sh
```

### Update Infrastructure

```bash
cd aws/terraform
terraform plan
terraform apply
```

### Database Migrations

Run as one-off ECS task (see Quick Start Step 6)

## Next Steps

1. ✅ Set up custom domain
2. ✅ Configure CloudFront CDN
3. ✅ Set up monitoring alerts
4. ✅ Enable auto-scaling
5. ✅ Configure CI/CD pipeline
6. ✅ Enable AWS WAF

## Support

For issues:
1. Check CloudWatch logs
2. Verify security groups
3. Review task definition
4. Check health endpoint

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

