# Dragon Intelligence Platform - Start Script
# Start Ollama, Backend, and Frontend safely

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "🐉 Starting Dragon Intel Offline Startup Sequence" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if MongoDB is running
Write-Host "[*] Checking MongoDB connection..." -ForegroundColor Yellow
$mongoTest = try { $null = New-Object System.Net.Sockets.TcpClient('127.0.0.1', 27017); $true } catch { $false }
if (-not $mongoTest) {
    Write-Host "[!] WARNING: MongoDB not detected on localhost:27017" -ForegroundColor Red
    Write-Host "    Make sure MongoDB is running before using the application." -ForegroundColor Yellow
    Write-Host ""
}

# Start Ollama
Write-Host "[1/3] Starting Ollama Engine (llama3.2)..." -ForegroundColor Green
$ollamaProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama run llama3.2" -PassThru
Start-Sleep -Seconds 2

# Start Backend
Write-Host "[2/3] Starting Backend (Flask) on http://localhost:5000..." -ForegroundColor Green
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot\backend; .\.venv\Scripts\activate; python app.py" -PassThru
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[3/3] Starting Frontend (React) on http://localhost:3000..." -ForegroundColor Green
cd "$PSScriptRoot\frontend"
npm start

# Cleanup
Write-Host ""
Write-Host "Stopping services..." -ForegroundColor Yellow
Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
Stop-Process -Id $ollamaProcess.Id -ErrorAction SilentlyContinue