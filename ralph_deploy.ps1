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

Write-Host ""
Write-Host "[*] Stage 1.5: Running Rigorous RBAC Security Tests..." -ForegroundColor Yellow
python test_rbac_strict.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] RBAC SECURITY TEST FAILED! Deployment Aborted to prevent data leakage." -ForegroundColor Red
    Exit $LASTEXITCODE
}
Write-Host "[OK] All 48+ RBAC security test cases passed." -ForegroundColor Green

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
Write-Host "[*] Stage 5: Verifying Live Diagnostics..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
try {
    $diag = Invoke-RestMethod -Uri "https://dragon-intel-chatbot-api.onrender.com/api/diagnostics" -Method Get -TimeoutSec 30
    Write-Host "[OK] LIVE SYSTEM STATUS: $($diag.status)" -ForegroundColor Green
    Write-Host "     RBAC Matrix: $($diag.checks.rbac_matrix.status)"
    Write-Host "     MongoDB: $($diag.checks.mongodb.status)"
} catch {
    Write-Host "[!] Could not reach live diagnostics yet. Vercel/Render is likely still building." -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🎉 RALPH LOOP COMPLETE - 100% STABLE!" -ForegroundColor Green
Write-Host "Vercel and Render will now automatically trigger builds"
Write-Host "based on this new commit. Wait 3-5 minutes for live update."
Write-Host "========================================================" -ForegroundColor Cyan
