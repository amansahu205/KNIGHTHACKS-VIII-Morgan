# Start Backend Server with Environment Variables
# This script loads .env and starts the FastAPI server

Write-Host "🚀 Starting Backend Server..." -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and add your API keys" -ForegroundColor Yellow
    exit 1
}

# Load environment variables from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        # Remove quotes if present
        $value = $value -replace "^['`"]|['`"]$"
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
        Write-Host "✅ Loaded: $name" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🔧 Starting uvicorn server..." -ForegroundColor Cyan
Write-Host "📍 Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to backend directory and start server
Set-Location backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
