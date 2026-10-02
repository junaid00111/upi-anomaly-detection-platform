Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; uvicorn api.main:app --reload --port 8002"

Set-Location "$PSScriptRoot\dashboard"
npm run dev