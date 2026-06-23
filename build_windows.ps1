# PowerShell-Skript zum Erstellen einer Windows-EXE für Dino Run
# Ausführen mit: .\build_windows.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

function Ensure-Python {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) {
        Write-Error "Python ist nicht installiert oder nicht im PATH. Bitte installiere Python 3."
        exit 1
    }
    return $py.Source
}

function Create-Venv {
    if (-not (Test-Path .venv)) {
        Write-Host "Erstelle virtuelle Umgebung..."
        & $python -m venv .venv
    }
}

function Activate-Venv {
    $activatePath = Join-Path $root '.venv\Scripts\Activate.ps1'
    if (-not (Test-Path $activatePath)) {
        Write-Error "Aktivierungsskript nicht gefunden: $activatePath"
        exit 1
    }
    Write-Host "Aktiviere virtuelle Umgebung..."
    & $activatePath
}

$python = Ensure-Python
Create-Venv

Write-Host "Aktiviere virtuelle Umgebung..."
& "$root\.venv\Scripts\Activate.ps1"

Write-Host "Aktualisiere pip..."
& "$root\.venv\Scripts\python.exe" -m pip install --upgrade pip

Write-Host "Installiere Abhängigkeiten..."
& "$root\.venv\Scripts\python.exe" -m pip install --only-binary :all: -r requirements.txt

Write-Host "Erstelle Windows EXE mit PyInstaller..."
& "$root\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --onefile --windowed `
    --name "DinoRun" `
    --collect-all pygame `
    --add-data "images;images" `
    --add-data "levels;levels" `
    --add-data "music;music" `
    --add-data "sounds;sounds" `
    main.py

Write-Host "Build fertig. Die erzeugte EXE liegt in dist\DinoRun.exe"