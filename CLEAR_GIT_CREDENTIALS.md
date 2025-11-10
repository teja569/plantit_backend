# Clear Cached Git Credentials

The error shows you're still authenticated as `tej5859` but need to authenticate as `teja569`.

## Quick Fix: Clear Windows Credentials

### Method 1: Using Command Line

```powershell
# List all stored credentials
cmdkey /list

# Delete GitHub credentials (if found)
cmdkey /delete:git:https://github.com

# Or delete all git-related credentials
cmdkey /delete:LegacyGeneric:target=git:https://github.com
```

### Method 2: Using Windows Credential Manager (GUI)

1. Press `Win + R`
2. Type: `control /name Microsoft.CredentialManager`
3. Click **"Windows Credentials"**
4. Find any entries with `github.com` or `git:`
5. Click **"Remove"** for each one

### Method 3: Clear via Git

```powershell
# Clear git credential cache
git credential-manager-core erase

# Then type these lines (press Enter after each):
protocol=https
host=github.com
# Press Enter twice to finish
```

## After Clearing Credentials

1. **Create Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic) with `repo` scope
   - Copy the token

2. **Push Again:**
   ```powershell
   git push -u origin main
   ```
   - Username: `teja569`
   - Password: **Paste your Personal Access Token**

3. **Or Update Remote with Token:**
   ```powershell
   git remote set-url origin https://teja569:YOUR_TOKEN@github.com/teja569/plantit_backend.git
   git push -u origin main
   ```

## Verify Current User

```powershell
# Check git config
git config --global user.name
git config --global user.email

# Should show:
# teja569
# tejasaii1729@gmail.com
```

## Alternative: Use SSH (No Password Issues)

If you keep having authentication issues, use SSH:

```powershell
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "tejasaii1729@gmail.com"

# 2. Copy public key
cat ~/.ssh/id_ed25519.pub

# 3. Add to GitHub: https://github.com/settings/keys

# 4. Update remote to SSH
git remote set-url origin git@github.com:teja569/plantit_backend.git

# 5. Push
git push -u origin main
```

