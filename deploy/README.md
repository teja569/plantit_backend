# EC2 Deployment Scripts

Quick deployment to EC2 Ubuntu server.

## Files

- `setup-server.sh` - Initial server setup (run once)
- `ec2-deploy.sh` - Deploy application to server
- `plant-delivery-api.service` - Systemd service file
- `nginx.conf` - Nginx reverse proxy configuration

## Quick Start

1. **Setup server** (first time only):
   ```bash
   chmod +x deploy/setup-server.sh
   ./deploy/setup-server.sh
   ```

2. **Create .env file on server**:
   ```bash
   ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
   sudo nano /opt/plant-delivery-api/.env
   # Add your environment variables
   ```

3. **Deploy application**:
   ```bash
   chmod +x deploy/ec2-deploy.sh
   ./deploy/ec2-deploy.sh
   ```

## Production URL

After deployment:
- **API**: http://3.111.165.191/api/v1
- **Health**: http://3.111.165.191/health
- **Docs**: http://3.111.165.191/docs

See `EC2_DEPLOYMENT.md` for detailed instructions.

