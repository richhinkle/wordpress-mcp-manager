# Create Fresh Repository Script
# This creates a new repo with clean history

Write-Host "🔄 Creating fresh repository with clean history..." -ForegroundColor Green

# Create backup of current state
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_$timestamp"

Write-Host "Creating backup in $backupDir..." -ForegroundColor Cyan
Copy-Item -Path "." -Destination "../$backupDir" -Recurse -Exclude ".git"

# Remove git history
Write-Host "Removing old git history..." -ForegroundColor Yellow
Remove-Item -Path ".git" -Recurse -Force

# Initialize new repository
Write-Host "Initializing new repository..." -ForegroundColor Green
git init
git add .
git commit -m "Initial commit with cleaned codebase

- Removed hardcoded credentials
- Added proper environment variable usage
- Enhanced security practices"

Write-Host "✅ Fresh repository created!" -ForegroundColor Green
Write-Host "📁 Backup saved in: ../$backupDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add your remote: git remote add origin <your-repo-url>" -ForegroundColor White
Write-Host "2. Push clean history: git push -u origin main" -ForegroundColor White