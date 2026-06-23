#!/usr/bin/env bash
set -euo pipefail

# Basisverzeichnis des Projekts
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PYTHON=python3
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Fehler: Python 3 wird benötigt. Bitte installiere Python 3 zuerst."
  exit 1
fi

# Virtuelle Umgebung erstellen
if [ ! -d ".venv" ]; then
  echo "Erstelle virtuelle Umgebung..."
  "$PYTHON" -m venv .venv
fi

# Aktivieren der Umgebung
if [ -f ".venv/bin/activate" ]; then
  # POSIX / macOS
  # shellcheck source=/dev/null
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  # Windows Git Bash / MSYS
  # shellcheck source=/dev/null
  source .venv/Scripts/activate
else
  echo "Fehler: Aktivierungsskript der virtuellen Umgebung wurde nicht gefunden."
  exit 1
fi

echo "Aktualisiere pip..."
pip install --upgrade pip

echo "Installiere Abhängigkeiten..."
if ! command -v pkg-config >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    echo "pkg-config wird benötigt. Installiere pkg-config und sdl2 via Homebrew..."
    brew install pkg-config sdl2
  else
    echo "Warnung: pkg-config nicht gefunden. Bei fehlenden pygame-Binaries kann die Installation fehlschlagen."
  fi
fi
pip install --only-binary :all: -r requirements.txt

echo "Abhängigkeiten installiert."

echo "Verfügbare Befehle:"
echo "  ./install.sh            -> installiert Abhängigkeiten"
echo "  ./install.sh build      -> erstellt Paket für das aktuelle System"

target="${1:-}"
if [ "$target" = "build" ]; then
  if [[ "$OSTYPE" == darwin* ]]; then
    echo "Erstelle macOS App..."
    pyinstaller --noconfirm --windowed --onedir \
      --name "DinoRun" \
      --collect-all pygame \
      --collect-submodules pygame \
      --hidden-import pygame._sdl2 \
      --hidden-import pygame._sdl2.video \
      --hidden-import pygame._sdl2.mixer \
      --add-data "images:images" \
      --add-data "levels:levels" \
      --add-data "music:music" \
      --add-data "sounds:sounds" \
      main.py
    echo "Fertig. Mac-App liegt in dist/DinoRun.app oder dist/DinoRun."
  elif [[ "$OSTYPE" == msys* || "$OSTYPE" == cygwin* || "$OSTYPE" == win32* ]]; then
    echo "Erstelle Windows EXE..."
    pyinstaller --noconfirm --onefile --windowed \
      --name "DinoRun" \
      --collect-all pygame \
      --add-data "images;images" \
      --add-data "levels;levels" \
      --add-data "music;music" \
      --add-data "sounds;sounds" \
      main.py
    echo "Fertig. Windows EXE liegt in dist/DinoRun.exe."
  else
    echo "Unbekanntes Betriebssystem: $OSTYPE"
    echo "Bitte nutze PyInstaller direkt oder führe dieses Skript auf macOS/Windows aus."
    exit 1
  fi
fi
