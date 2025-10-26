# Start Frontend Server
# This script starts the Next.js development server

Write-Host "🚀 Starting Frontend Server..." -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "❌ Error: node_modules not found!" -ForegroundColor Red
    Write-Host "Please run: cd frontend && npm install --legacy-peer-deps" -ForegroundColor Yellow
    exit 1
}

# Check if .env.local exists
if (-not (Test-Path "frontend\.env.local")) {
    Write-Host "⚠️  Warning: frontend\.env.local not found!" -ForegroundColor Yellow
    Write-Host "API calls will use default URL" -ForegroundColor Yellow
}

Write-Host "🔧 Starting Next.js development server..." -ForegroundColor Cyan
Write-Host "📍 Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to frontend directory and start server
Set-Location frontend
npm run dev
