# GitHub Deployment Guide

Complete guide for setting up GitHub CLI, cleaning git history, and deploying your WordPress MCP Manager to GitHub.

## Prerequisites

- Git installed and configured
- Python project with git repository
- Windows PowerShell or Command Prompt access

## Step 1: Install GitHub CLI

### Option A: Download from GitHub
1. Visit https://cli.github.com/
2. Download the Windows installer (.msi file)
3. Run the installer with administrator privileges
4. Follow the installation wizard

### Option B: Using Package Manager (if you have one)
```powershell
# Using Chocolatey
choco install gh

# Using Scoop
scoop install gh

# Using Winget
winget install --id GitHub.cli
```

### Verify Installation
Open a new command prompt and test:
```cmd
gh --version
```
You should see something like: `gh version 2.81.0 (2025-10-01)`

## Step 2: Authenticate with GitHub

```powershell
gh auth login
```

Follow the prompts:
1. Choose "GitHub.com"
2. Select "HTTPS" for Git protocol
3. Choose "Yes" to authenticate Git with GitHub credentials
4. Select "Login with a web browser"
5. Copy the one-time code shown
6. Press Enter to open browser
7. Paste the code and complete authentication

## Step 3: Clean Git History (If Needed)

⚠️ **Only if your repository contains exposed secrets/PII**

### Install git-filter-repo
```powershell
# Exit virtual environment first
deactivate

# Install globally
pip install git-filter-repo
```

### Create Secrets Replacement File
Create `secrets.txt` with your actual exposed secrets:
```
YOUR_ACTUAL_EXPOSED_TOKEN==>your-access-token-here
https://your-actual-domain.com==>https://your-wordpress-site.com
your-actual-domain.com==>your-wordpress-site.com
```

### Run History Cleanup
```powershell
# Create backup branch
git branch backup-before-cleanup

# Clean history
git-filter-repo --replace-text secrets.txt --force

# Delete secrets file immediately
Remove-Item secrets.txt
```

## Step 4: Prepare Repository

### Update .gitignore
Ensure these entries are in your `.gitignore`:
```gitignore
# Environment files
.env
.env.local
.env.production

# Cache and data
cache/
data/

# Security files
*.key
*.pem
*.p12
secrets.txt
config.json
secrets.json

# Scripts with potential secrets
*.ps1
```

### Commit Final Changes
```powershell
git add .gitignore
git commit -m "Final security updates before GitHub deployment"
```

## Step 5: Create GitHub Repository

### Using GitHub CLI
```powershell
gh repo create your-project-name --public --description "Your project description" --clone=false
```

Example:
```powershell
gh repo create wordpress-mcp-manager --public --description "WordPress MCP Manager - Flask web app for managing WordPress sites through AIWU MCP with Instagram integration" --clone=false
```

### Alternative: Manual Creation
1. Go to https://github.com/new
2. Enter repository name
3. Choose public/private
4. Don't initialize with README (you already have code)
5. Click "Create repository"

## Step 6: Connect and Push to GitHub

### Add Remote Origin
```powershell
git remote add origin https://github.com/yourusername/your-repo-name.git
```

### Push to GitHub
```powershell
# Push master branch
git push -u origin master

# Or if using main branch
git push -u origin main
```

## Step 7: Post-Deployment Security

### Regenerate Exposed Credentials
If you cleaned git history due to exposed secrets:

1. **WordPress MCP Token**:
   - Log into WordPress admin
   - Go to AIWU MCP plugin settings
   - Generate new access token
   - Update your local `.env` file

2. **API Keys**:
   - Regenerate any API keys that were exposed
   - Update `.env` file with new keys

3. **Passwords**:
   - Change any passwords that were hardcoded
   - Use application passwords for WordPress

### Update Local Environment
```powershell
# Copy environment template
cp .env.example .env

# Edit .env with your NEW credentials (never commit this file)
notepad .env
```

## Step 8: Verify Deployment

### Check Repository
1. Visit your GitHub repository URL
2. Verify all files are present
3. Check that no sensitive data is visible
4. Review commit history for cleanliness

### Test Application Locally
```powershell
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test with new credentials
python run.py
```

## Troubleshooting

### GitHub CLI Not Found
- Restart your terminal/PowerShell after installation
- Check if it's in a different location: `where gh`
- Use full path: `"C:\Program Files\GitHub CLI\gh.exe"`

### Authentication Issues
```powershell
# Check auth status
gh auth status

# Re-authenticate if needed
gh auth logout
gh auth login
```

### Git History Still Contains Secrets
If git-filter-repo didn't work:
1. Create fresh repository (nuclear option)
2. Copy clean files to new folder
3. Initialize new git repo
4. Push to GitHub

### Push Rejected
```powershell
# Force push (use with caution)
git push --force-with-lease origin master
```

## Security Checklist

Before pushing to GitHub, verify:
- [ ] No `.env` files committed
- [ ] No hardcoded passwords/tokens in source code
- [ ] No real domain names in examples
- [ ] Cache/data directories ignored
- [ ] Secrets replacement file deleted
- [ ] All exposed credentials regenerated

## Best Practices Going Forward

1. **Never commit sensitive data**
2. **Use environment variables for all secrets**
3. **Regular security audits of commits**
4. **Use placeholder values in documentation**
5. **Keep .gitignore updated**
6. **Review pull requests for PII**

## Repository Structure

Your final GitHub repository should look like:
```
your-repo/
├── .gitignore          # Comprehensive ignore rules
├── .env.example        # Template with placeholders
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── run.py             # Application entry point
├── src/               # Source code
├── static/            # Frontend assets
├── docs/              # Documentation
└── tests/             # Test files
```

## Success Indicators

✅ Repository created on GitHub  
✅ Clean git history (no exposed secrets)  
✅ All functionality preserved  
✅ Proper .gitignore in place  
✅ Environment variables used correctly  
✅ Documentation updated  
✅ Application runs with new credentials  

Your WordPress MCP Manager is now safely deployed to GitHub with professional security practices!