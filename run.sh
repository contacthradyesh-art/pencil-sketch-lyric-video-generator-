#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
mkdir -p input output assets temp/frames
command -v python3 >/dev/null || { echo "Python 3 is required."; exit 1; }
command -v node >/dev/null || { echo "Node.js 20+ is required."; exit 1; }
if ! command -v ffmpeg >/dev/null; then
  echo "Installing FFmpeg…"
  sudo apt-get update && sudo apt-get install -y ffmpeg
fi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
npm install --no-audit --no-fund
if [[ "${1:-}" == "--render" ]]; then
  shift
  python src/main.py "$@"
else
  echo "Starting Pencil Sketch Studio at http://localhost:8000"
  echo "In Codespaces, open forwarded port 8000."
  exec python -m src.server
fi
