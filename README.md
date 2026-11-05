# Pencil Sketch Lyric Video Generator
Headless lyric-video pipeline for GitHub Codespaces and local Linux.

## Inputs
Place the original song at input/song.mp3 and UTF-8 lyrics at input/lyrics.txt (one sung line per row). The final video uses the original song audio.

## Run
Ubuntu/Codespaces:
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg python3-venv
bash run.sh
```
First run downloads Demucs/WhisperX models and may take a while. Python 3.10/3.11 and Node 20+ are recommended. CPU is the portable default; a small Codespace may run slowly or run out of memory.

## Configuration
Set LANGUAGE=en or hi, DEVICE=cpu or cuda, FPS=30, WIDTH=1920, HEIGHT=1080. Output: output/final_video.mp4.

WhisperX forced alignment is used for word timestamps. The pipeline fails when alignment coverage is below 98%; it does not distribute or invent missing timestamps. Check lyrics spelling, repeated choruses, and language setting.

Optional licensed font: assets/Caveat-Regular.ttf. Optional texture: assets/paper-texture.jpg. Only add assets you have permission to use.
