# Fix Render CLI Conflict

You're encountering a conflict where `render` command is being interpreted as a templating engine instead of Render CLI.

## Solution 1: Use Full Command Path (Quick Fix)

Instead of `render`, use the full path or npx:

```powershell
# Use npx to run render-cli
npx render-cli login
npx render-cli services:create --config render.yaml
npx render-cli deploy
```

## Solution 2: Uninstall Conflicting Package

Check if there's a conflicting `render` package:

```powershell
npm list -g render
```

If it exists, uninstall it:

```powershell
npm uninstall -g render
```

Then verify render-cli works:

```powershell
render-cli login
```

## Solution 3: Use Render CLI Directly

The Render CLI might be installed as `render-cli` instead of `render`:

```powershell
# Try this instead
render-cli login
render-cli services:create --config render.yaml
render-cli deploy
```

## Solution 4: Create Alias (Windows PowerShell)

Create a PowerShell alias:

```powershell
# Add to your PowerShell profile
Set-Alias -Name render -Value render-cli

# Or create a function
function render { render-cli $args }
```

## Solution 5: Use Alternative Deployment Method

If CLI continues to have issues, use the Render Dashboard:

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Choose "Deploy existing image" or connect via GitLab/Bitbucket
4. Manually configure using the settings from `render.yaml`

## Recommended: Use npx (No Installation Conflicts)

```powershell
# Login
npx render-cli login

# Create service
npx render-cli services:create --config render.yaml

# Deploy
npx render-cli deploy

# Set environment variables
npx render-cli env:set SECRET_KEY="your-key"
```

This avoids global installation conflicts.

