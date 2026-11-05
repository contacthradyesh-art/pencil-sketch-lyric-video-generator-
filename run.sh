#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
mkdir -p input output assets temp/frames
command -v ffmpeg >/dev/null || { sudo apt-get update && sudo apt-get install -y ffmpeg; }
command -v python3 >/dev/null || { echo "Python 3 required"; exit 1; }
command -v node >/dev/null || { echo "Node.js required"; exit 1; }
python3 -m venv .venv || true
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm install --no-audit --no-fund
[[ -s input/song.mp3 ]] || { echo "Add input/song.mp3 first"; exit 1; }
[[ -s input/lyrics.txt ]] || { echo "Add input/lyrics.txt first"; exit 1; }
python src/main.py "$@"
