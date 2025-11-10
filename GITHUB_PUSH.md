# Push to GitHub - Step by Step

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `nexus` (or your preferred name)
3. Description: "FastAPI Plant Delivery API"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

## Step 2: Add Remote and Push

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nexus.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Authentication

If prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

### Create Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `render-deployment`
4. Select scopes: **`repo`** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

## Alternative: Using SSH (Recommended for Future)

If you want to use SSH instead:

```bash
# Add SSH remote
git remote set-url origin git@github.com:YOUR_USERNAME/nexus.git

# Push
git push -u origin main
```

## Quick Commands Summary

```bash
# 1. Initialize (already done)
git init
git add .
git commit -m "Initial commit"

# 2. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/nexus.git

# 3. Push
git push -u origin main
```

## After Pushing to GitHub

Once pushed, you can:

1. **Deploy to Render via GitHub:**
   - Go to Render Dashboard
   - Connect to GitHub
   - Select your repository
   - Render will auto-detect `render.yaml`

2. **Update code:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/nexus.git
```

### Authentication failed
- Use Personal Access Token instead of password
- Or set up SSH keys

### "branch main does not exist"
```bash
git branch -M main
git push -u origin main
```

