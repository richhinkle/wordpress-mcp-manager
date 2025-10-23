# Git History Cleanup Guide

## ⚠️ SECURITY WARNING
Your git history contains exposed credentials that need to be removed.

## Method 1: git-filter-repo (Recommended)

### Step 1: Install git-filter-repo globally
```powershell
# Exit venv first
deactivate

# Install globally
pip install git-filter-repo
```

### Step 2: Create replacement file
Create a file called `secrets.txt` with your actual secrets to replace:
```
YOUR_ACTUAL_TOKEN_HERE==>your-access-token-here
https://YOUR_ACTUAL_DOMAIN.com==>https://your-wordpress-site.com
YOUR_ACTUAL_DOMAIN.com==>your-wordpress-site.com
```

### Step 3: Run cleanup
```powershell
# Create backup
git branch backup-before-cleanup

# Run filter-repo
git-filter-repo --replace-text secrets.txt --force

# Clean up
Remove-Item secrets.txt
```

### Step 4: Force push
```powershell
git push --force-with-lease origin main
```

## Method 2: Fresh Repository (Safest)

If you don't need the commit history:

```powershell
# Backup current state
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path "." -Destination "../backup_$timestamp" -Recurse -Exclude ".git"

# Remove git history
Remove-Item -Path ".git" -Recurse -Force

# Start fresh
git init
git add .
git commit -m "Initial commit with cleaned codebase"
git remote add origin <your-repo-url>
git push -u origin main
```

## What Needs to be Replaced

Replace these patterns in your secrets.txt file with YOUR actual values:
- `YOUR_ACTUAL_TOKEN_HERE` - Your WordPress MCP access token
- `YOUR_ACTUAL_DOMAIN.com` - Your WordPress domain

## Verification

After cleanup, verify secrets are gone:
```powershell
# Check recent commits
git log --oneline -5

# Search for old secrets (should return nothing)
git log --all --full-history -- "*" | Select-String "YOUR_OLD_TOKEN"
```

## Important Notes

1. **Never put actual secrets in scripts or documentation**
2. **Always create backups before history rewriting**
3. **Regenerate any exposed credentials immediately**
4. **Force push will affect collaborators - coordinate with team**