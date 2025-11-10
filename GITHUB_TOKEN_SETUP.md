# GitHub Authentication Setup

## Important: GitHub No Longer Accepts Passwords

GitHub requires a **Personal Access Token** instead of your password.

## Step 1: Create Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Token name**: `plantit-deployment`
4. **Expiration**: Choose 90 days or custom
5. **Select scopes**: Check **`repo`** (Full control of private repositories)
6. Click **"Generate token"**
7. **IMPORTANT**: Copy the token immediately (you won't see it again!)

## Step 2: Use Token to Push

### Option A: Enter Token When Prompted

```bash
git push -u origin main
```

When prompted:
- **Username**: `teja569`
- **Password**: **Paste your Personal Access Token** (not your GitHub password)

### Option B: Update Remote with Token (Easier)

```bash
# Replace YOUR_TOKEN with the token you just created
git remote set-url origin https://teja569:YOUR_TOKEN@github.com/teja569/plantit_backend.git

# Now push (no authentication prompt)
git push -u origin main
```

### Option C: Use SSH (Most Secure, Recommended for Future)

1. **Generate SSH Key:**
   ```bash
   ssh-keygen -t ed25519 -C "tejasai@spotmies.ai"
   ```
   - Press Enter to accept default location
   - Optionally set a passphrase

2. **Copy Public Key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy the output

3. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click **"New SSH key"**
   - Title: `My Computer`
   - Key: Paste your public key
   - Click **"Add SSH key"**

4. **Update Remote to SSH:**
   ```bash
   git remote set-url origin git@github.com:teja569/plantit_backend.git
   git push -u origin main
   ```

## Current Git Configuration

✅ **User Name**: `teja569` (updated)
✅ **Email**: `tejasai@spotmies.ai`
✅ **Remote**: `https://github.com/teja569/plantit_backend.git`

## Quick Command Summary

**Using Token (Easiest):**
```bash
# 1. Create token at https://github.com/settings/tokens
# 2. Update remote with token
git remote set-url origin https://teja569:YOUR_TOKEN@github.com/teja569/plantit_backend.git

# 3. Push
git push -u origin main
```

**Using SSH (Most Secure):**
```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "tejasai@spotmies.ai"

# 2. Add to GitHub (copy ~/.ssh/id_ed25519.pub)

# 3. Update remote
git remote set-url origin git@github.com:teja569/plantit_backend.git

# 4. Push
git push -u origin main
```

## Troubleshooting

### "Permission denied"
- Make sure you're using a Personal Access Token, not password
- Verify token has `repo` scope
- Check token hasn't expired

### "Repository not found"
- Verify repository exists: https://github.com/teja569/plantit_backend
- Check you have access to the repository

### Clear Cached Credentials
```bash
# Windows Credential Manager
cmdkey /list | findstr git
# Delete the GitHub entry if needed
```

## After Successful Push

Once pushed successfully:
- ✅ Code is on GitHub
- ✅ You can deploy to Render via GitHub
- ✅ Future pushes: `git add .`, `git commit -m "message"`, `git push`

