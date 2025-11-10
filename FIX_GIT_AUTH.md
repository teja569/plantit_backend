# Fix Git Authentication Issue

## Problem
You're authenticated as `tej5859` but trying to push to `teja569/plantit_backend.git`

## Solution Options

### Option 1: Use Personal Access Token (Recommended)

GitHub no longer accepts passwords. You need a Personal Access Token:

1. **Create Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `plantit-deployment`
   - Select scope: **`repo`** (full control)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Use Token When Pushing:**
   ```bash
   git push -u origin main
   ```
   - Username: `teja569`
   - Password: **Paste your Personal Access Token**

3. **Or Update Remote with Token:**
   ```bash
   git remote set-url origin https://teja569:YOUR_TOKEN@github.com/teja569/plantit_backend.git
   git push -u origin main
   ```

### Option 2: Update Git User Configuration

If `teja569` is your account:

```bash
# Set git user to match repository owner
git config --global user.name "teja569"
git config --global user.email "your-email@example.com"
```

### Option 3: Use SSH (Most Secure)

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

2. **Add to GitHub:**
   - Copy public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to https://github.com/settings/keys
   - Click "New SSH key"
   - Paste your key

3. **Update Remote:**
   ```bash
   git remote set-url origin git@github.com:teja569/plantit_backend.git
   git push -u origin main
   ```

### Option 4: Clear Cached Credentials

If old credentials are cached:

```bash
# Clear Windows credential manager
git credential-manager-core erase
# Then enter:
# protocol=https
# host=github.com
# (Press Enter twice)

# Or clear all git credentials
git config --global --unset credential.helper
git config --global credential.helper manager-core
```

## Quick Fix (Recommended)

1. **Create Personal Access Token** (see Option 1)
2. **Update remote with token:**
   ```bash
   git remote set-url origin https://teja569:YOUR_TOKEN@github.com/teja569/plantit_backend.git
   ```
3. **Push:**
   ```bash
   git push -u origin main
   ```

## Verify Configuration

```bash
# Check git user
git config --global user.name
git config --global user.email

# Check remote
git remote -v
```

## After Successful Push

Once pushed, you can:
- Deploy to Render via GitHub
- Update code with: `git add .`, `git commit -m "message"`, `git push`

