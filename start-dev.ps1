# Move to project root
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Starting UPI Data Pipeline" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Run the data pipeline first
python src/pipeline.py

# Stop if pipeline fails
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Pipeline failed. Dashboard will not start." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Pipeline completed successfully." -ForegroundColor Green

# Start FastAPI backend
Write-Host ""
Write-Host "Starting FastAPI backend on port 8002..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; uvicorn api.main:app --reload --port 8002"

# Start dashboard
Write-Host ""
Write-Host "Starting dashboard..." -ForegroundColor Cyan

Set-Location "$PSScriptRoot\dashboard"
npm run dev