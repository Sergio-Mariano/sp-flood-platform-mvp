# start_app.ps1 — inicia o app local (uvicorn) com venv
$ErrorActionPreference = 'Stop'
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BASE

if (!(Test-Path ".\.venv\Scripts\Activate.ps1")) {
  $py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
  if (!(Test-Path $py)) { $py = "python" }
  & $py -m venv .venv
}

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& .\.venv\Scripts\Activate.ps1

pip install -e .
pip install "uvicorn[standard]" fastapi httpx "psycopg[binary]" jinja2 python-multipart apscheduler

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
