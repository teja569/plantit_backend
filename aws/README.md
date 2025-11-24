# AWS Deployment Guide

This guide will help you deploy the Plant Delivery API to AWS using ECS Fargate, RDS PostgreSQL, and other AWS services.

## Architecture Overview

- **ECS Fargate**: Container orchestration (serverless containers)
- **RDS PostgreSQL**: Managed database
- **Application Load Balancer**: Traffic distribution and SSL termination
- **S3**: Static file storage
- **CloudWatch**: Logging and monitoring
- **Secrets Manager**: Secure credential storage
- **ECR**: Docker image registry

## Prerequisites

1. AWS CLI installed and configured
2. Terraform >= 1.0 (for infrastructure)
3. Docker installed
4. AWS account with appropriate permissions
5. Domain name and SSL certificate (optional but recommended)

## Quick Start

### 1. Set Up AWS Secrets

```bash
cd aws
chmod +x setup-secrets.sh
./setup-secrets.sh
```

This will create secrets in AWS Secrets Manager for:
- Database URL
- Secret Key (JWT)
- Gemini API Key
- AWS Credentials
- Cloudinary (optional)
- SendGrid (optional)

### 2. Deploy Infrastructure with Terraform

```bash
cd terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Apply infrastructure
terraform apply
```

This will create:
- VPC with public/private subnets
- RDS PostgreSQL database
- ECS cluster
- Application Load Balancer
- ECR repository
- S3 bucket
- Security groups
- IAM roles

### 3. Build and Push Docker Image

```bash
cd ../..

# Build image
docker build -t plant-delivery-api:latest .

# Tag for ECR (replace with your ECR URI from terraform output)
docker tag plant-delivery-api:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plant-delivery-api:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/plant-delivery-api:latest
```

### 4. Create ECS Task Definition

Update `ecs-task-definition.json` with:
- Your AWS account ID
- Your region
- Secret ARNs from Secrets Manager

Then register the task definition:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### 5. Create ECS Service

```bash
aws ecs create-service \
  --cluster plant-delivery-api-cluster \
  --service-name plant-delivery-api-service \
  --task-definition plant-delivery-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/plant-delivery-api-tg/xxx,containerName=plant-delivery-api,containerPort=8000" \
  --health-check-grace-period-seconds 60
```

### 6. Run Database Migrations

```bash
# Create a one-off task for migrations
aws ecs run-task \
  --cluster plant-delivery-api-cluster \
  --task-definition plant-delivery-api \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "plant-delivery-api",
      "command": ["alembic", "upgrade", "head"]
    }]
  }'
```

## Automated Deployment

### Using Deployment Script

```bash
chmod +x aws/deploy.sh
export AWS_REGION=us-east-1
export ECR_REPO=plant-delivery-api
export ECS_CLUSTER=plant-delivery-api-cluster
export ECS_SERVICE=plant-delivery-api-service
./aws/deploy.sh
```

### Using GitHub Actions

1. Set up GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

2. Push to `main` or `production` branch to trigger deployment

## Environment Variables

The application uses AWS Secrets Manager for sensitive values. Update the task definition to reference secrets:

```json
{
  "secrets": [
    {
      "name": "DATABASE_URL",
      "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:plant-delivery-api/database-url"
    }
  ]
}
```

## Configuration

### Database Connection

The application automatically detects AWS RDS and configures SSL. Ensure your `DATABASE_URL` in Secrets Manager is in the format:

```
postgresql://username:password@rds-endpoint:5432/database?sslmode=require
```

### S3 Configuration

Update your environment variables to use S3 for file storage:

```python
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_BUCKET_NAME=plant-delivery-api-static-production
AWS_REGION=us-east-1
```

### CORS Configuration

Set `ALLOWED_ORIGINS` in Secrets Manager or environment variables:

```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Monitoring

### CloudWatch Logs

Logs are automatically sent to CloudWatch:
- Log Group: `/ecs/plant-delivery-api`
- Retention: 30 days (configurable)

### Health Checks

The application exposes a `/health` endpoint that:
- Checks database connectivity
- Verifies Gemini API status
- Returns system status

### CloudWatch Metrics

ECS automatically sends metrics:
- CPU utilization
- Memory utilization
- Task count
- Service health

## Scaling

### Auto Scaling

Create an auto-scaling target:

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/plant-delivery-api-cluster/plant-delivery-api-service \
  --min-capacity 2 \
  --max-capacity 10
```

Create scaling policy:

```bash
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/plant-delivery-api-cluster/plant-delivery-api-service \
  --policy-name cpu-scaling-policy \
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

1. Request SSL certificate in ACM (AWS Certificate Manager)
2. Update ALB listener to use certificate
3. Configure HTTPS redirect

### Security Groups

- ALB: Allow HTTP (80) and HTTPS (443) from internet
- ECS: Allow port 8000 from ALB only
- RDS: Allow PostgreSQL (5432) from ECS only

### IAM Roles

- ECS Execution Role: Pulls images, writes logs, reads secrets
- ECS Task Role: Accesses S3, other AWS services

## Troubleshooting

### Check ECS Service Status

```bash
aws ecs describe-services \
  --cluster plant-delivery-api-cluster \
  --services plant-delivery-api-service
```

### View Logs

```bash
aws logs tail /ecs/plant-delivery-api --follow
```

### Check Task Status

```bash
aws ecs list-tasks \
  --cluster plant-delivery-api-cluster \
  --service-name plant-delivery-api-service
```

### Connect to Database

```bash
# Get RDS endpoint from Terraform output
terraform output rds_endpoint

# Connect using psql
psql -h <rds-endpoint> -U postgres -d plantdelivery
```

## Cost Optimization

1. **Use Reserved Instances** for RDS (if predictable workload)
2. **Enable RDS Auto Scaling** for storage
3. **Use Spot Instances** for ECS (if fault-tolerant)
4. **Set up S3 Lifecycle Policies** for old files
5. **Enable CloudWatch Logs Retention** to avoid long-term storage costs

## Backup and Recovery

### RDS Backups

- Automated backups: 7 days retention
- Manual snapshots: Create before major changes

### Application Backups

- Database: RDS automated backups
- Static files: S3 versioning enabled
- Configuration: Terraform state in S3

## Updates and Maintenance

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

Run migrations as a one-off ECS task (see step 6 above)

## Support

For issues:
1. Check CloudWatch logs
2. Verify security groups
3. Check task definition and service configuration
4. Review health check endpoint

## Next Steps

1. Set up custom domain and SSL certificate
2. Configure CloudFront for CDN (optional)
3. Set up monitoring alerts
4. Configure auto-scaling
5. Set up CI/CD pipeline
6. Enable AWS WAF for additional security

