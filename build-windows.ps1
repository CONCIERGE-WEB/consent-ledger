$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

$python = Join-Path $root ".venv\Scripts\python.exe"
& $python -m pip install -r desktop-requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependências do executável." }

$env:SECRET_KEY = "desktop-build-only-random-secret-0123456789-abcdefgh-ABCDEFGH"
$env:DEBUG = "False"
& $python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar os arquivos estáticos." }

& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --console `
    --name ConsentLedger `
    --add-data "$root\staticfiles;staticfiles" `
    --hidden-import config.settings `
    --hidden-import config.urls `
    --hidden-import config.wsgi `
    --hidden-import ledger.admin `
    --hidden-import ledger.apps `
    --collect-all django `
    --collect-all axes `
    --collect-all whitenoise `
    --collect-all waitress `
    desktop_launcher.py
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar ConsentLedger.exe." }

Write-Host "Executável criado em $root\dist\ConsentLedger.exe"
