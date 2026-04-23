# PowerShell helper for backend (run from project root or backend).
# Usage: .\backend\manage.ps1 <command>   or from backend: .\manage.ps1 <command>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("start-db", "stop-db", "init", "migrate", "upgrade", "seed")]
    [string]$Command
)

$BackendDir = $PSScriptRoot
$ProjectRoot = (Resolve-Path (Join-Path $BackendDir "..")).Path

function Start-Db {
    Set-Location $ProjectRoot
    docker compose up -d
}

function Stop-Db {
    Set-Location $ProjectRoot
    docker compose down
}

function Invoke-InitDb {
    $env:FLASK_APP = "app.factory:app"
    Set-Location $BackendDir
    flask db init
}

function Invoke-Migrate {
    $env:FLASK_APP = "app.factory:app"
    Set-Location $BackendDir
    flask db migrate -m "init"
}

function Invoke-Upgrade {
    $env:FLASK_APP = "app.factory:app"
    Set-Location $BackendDir
    flask db upgrade
}

function Invoke-Seed {
    # Placeholder — no seed required yet
    Write-Host "Seed: placeholder (no seed data yet)."
}

switch ($Command) {
    "start-db"   { Start-Db }
    "stop-db"    { Stop-Db }
    "init"       { Invoke-InitDb }
    "migrate"    { Invoke-Migrate }
    "upgrade"    { Invoke-Upgrade }
    "seed"       { Invoke-Seed }
}
