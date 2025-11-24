# Quick Deploy to EC2

## Step 1: Save SSH Key

You have two options:

### Option A: Save key manually
1. Create file: `C:\Users\ADMIN\.ssh\AWS.pem`
2. Paste your private key content (the one you provided)
3. Save the file

### Option B: Use the script
```powershell
# The key content you provided should be saved to the file
# Then run:
powershell -ExecutionPolicy Bypass -File deploy/save-ssh-key.ps1
```

## Step 2: Deploy

Once the key is saved, run:

```powershell
powershell -ExecutionPolicy Bypass -File deploy/ec2-deploy.ps1
```

## What Happens

The deployment script will:
1. ✅ Setup server (install Python, Nginx, etc.)
2. ✅ Copy your .env file to server
3. ✅ Copy application files
4. ✅ Install Python dependencies
5. ✅ Configure systemd service
6. ✅ Configure Nginx
7. ✅ Run database migrations
8. ✅ Start the application

## Production URLs

After deployment:
- **API**: http://3.111.165.191/api/v1
- **Health**: http://3.111.165.191/health  
- **Docs**: http://3.111.165.191/docs

## Manual Steps (if script fails)

1. **Save SSH key** to `C:\Users\ADMIN\.ssh\AWS.pem`

2. **Test connection**:
   ```powershell
   ssh -i C:\Users\ADMIN\.ssh\AWS.pem ubuntu@3.111.165.191
   ```

3. **Copy .env file**:
   ```powershell
   scp -i C:\Users\ADMIN\.ssh\AWS.pem .env ubuntu@3.111.165.191:/tmp/
   ```

4. **SSH and setup**:
   ```bash
   ssh -i ~/.ssh/AWS.pem ubuntu@3.111.165.191
   sudo mv /tmp/.env /opt/plant-delivery-api/.env
   # Then follow manual deployment steps from EC2_DEPLOYMENT.md
   ```

## Need Help?

Check `deploy/EC2_DEPLOYMENT.md` for detailed instructions.

