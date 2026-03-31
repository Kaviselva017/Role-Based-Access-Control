# Dragon Intelligence Platform - Start Script
# Start both backend and frontend servers

Write-Host "Dragon Intelligence Platform - RBAC" -ForegroundColor Cyan
Write-Host ""

# Check if MongoDB is running
Write-Host "[*] Checking MongoDB connection..." -ForegroundColor Yellow
$mongoTest = try { $null = New-Object System.Net.Sockets.TcpClient('127.0.0.1', 27017); $true } catch { $false }
if (-not $mongoTest) {
    Write-Host "[!] WARNING: MongoDB not detected on localhost:27017" -ForegroundColor Red
    Write-Host "    Make sure MongoDB is running before using the application." -ForegroundColor Yellow
    Write-Host ""
}

# Start Backend
Write-Host "[1/2] Starting Backend (Flask) on http://localhost:5000" -ForegroundColor Green
Write-Host "    Press Ctrl+C to stop" -ForegroundColor DarkGray
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot\backend; python app.py" -PassThru
Start-Sleep -Seconds 2

# Start Frontend
Write-Host ""
Write-Host "[2/2] Starting Frontend (React) on http://localhost:3000" -ForegroundColor Green
Write-Host "    Press Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

cd "$PSScriptRoot\frontend"
npm start

# Cleanup
Write-Host ""
Write-Host "Stopping services..." -ForegroundColor Yellow
Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue