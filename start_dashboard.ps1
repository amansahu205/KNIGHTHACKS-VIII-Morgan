# Start Dashboard
# This script starts the dashboard on port 3001

Write-Host "🚀 Starting Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "dashboard\node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    Set-Location dashboard
    npm install
    Set-Location ..
}

Write-Host "✅ Starting dashboard server..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location dashboard
$env:PORT = "3001"
npm run dev
