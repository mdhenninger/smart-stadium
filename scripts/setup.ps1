# Smart Stadium - Setup Script
# Automated setup for development environment

echo "🏟️ Smart Stadium - Development Setup"
echo "====================================="

# Check Python installation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check Node.js installation
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found. Please install Node.js 16+ first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python and Node.js found" -ForegroundColor Green

# Create virtual environment
Write-Host "🔧 Creating Python virtual environment..."
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
Write-Host "📦 Installing Node.js dependencies..."
Set-Location "frontend\smart-stadium-dashboard"
npm install
Set-Location "..\..\"

Write-Host ""
Write-Host "✅ Smart Stadium setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start Smart Stadium:"
Write-Host "   Windows: .\scripts\start_smart_stadium.bat"
Write-Host "   PowerShell: .\scripts\start_smart_stadium.ps1"
Write-Host ""
Write-Host "📋 API Documentation: http://localhost:8000/api/docs"
Write-Host "🎮 Dashboard: http://localhost:3000"