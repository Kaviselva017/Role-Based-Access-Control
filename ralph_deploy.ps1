# RALPH LOOP - Automated Build, Test, and Deploy Cycle

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🚀 RALPH LOOP - Automated Pipeline Triggered!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[*] Stage 1: Running Pre-Deployment Code Checks..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\backend"
python -m py_compile app.py rag_system.py models.py prompt_templates.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] SYNTAX ERROR DETECTED! Deployment Aborted." -ForegroundColor Red
    Exit $LASTEXITCODE
}
Write-Host "[OK] Code syntax checks passed." -ForegroundColor Green
Set-Location -Path "$PSScriptRoot"

Write-Host ""
Write-Host "[*] Stage 2: Staging all files for deployment..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "[*] Stage 3: Committing with automated tag..." -ForegroundColor Yellow
$commitMsg = Read-Host "Enter commit message (or press enter for 'Auto-Ralph Deployment')"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Auto-Ralph Deployment"
}
git commit -m "$commitMsg"

Write-Host ""
Write-Host "[*] Stage 4: Pushing to GitHub (origin main)..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🎉 PUSH COMPLETE!" -ForegroundColor Green
Write-Host "Vercel and Render will now automatically trigger builds"
Write-Host "based on this new commit. Wait 3-5 minutes for live update."
Write-Host "========================================================" -ForegroundColor Cyan
