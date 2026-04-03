@echo off
echo ========================================================
echo 🚀 RALPH LOOP - Automated Build, Test, and Deploy Cycle
echo ========================================================
echo.

echo [*] Stage 1: Running Pre-Deployment Code Checks...
cd backend
python -m py_compile app.py rag_system.py models.py prompt_templates.py
IF %ERRORLEVEL% NEQ 0 (
    echo [X] SYNTAX ERROR DETECTED! Deployment Aborted.
    exit /b %ERRORLEVEL%
)
echo [OK] Code syntax checks passed.
cd ..

echo [*] Stage 2: Staging all files for deployment...
git add .

echo [*] Stage 3: Committing with automated Ralph Loop tag...
set /p msg="Enter commit message (or press enter for 'Auto-Ralph Deployment'): "
if "%msg%"=="" set msg=Auto-Ralph Deployment
git commit -m "%msg%"

echo [*] Stage 4: Pushing to GitHub (origin main)...
git push origin main

echo.
echo ========================================================
echo 🎉 PUSH COMPLETE!
echo Vercel and Render will now automatically trigger builds
echo based on this new commit. Wait 3-5 minutes for live update.
echo ========================================================
pause
