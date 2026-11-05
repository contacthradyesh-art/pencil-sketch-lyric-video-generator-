# Pencil Sketch Studio AI

A mobile-friendly web studio and video-editing workspace for creating pencil-sketch lyric videos. It combines Demucs vocal separation, WhisperX forced alignment, a Canvas sketch renderer, Puppeteer and FFmpeg.

## Current scope
- Browser-based project creation and upload UI.
- Visual style selection: cinematic, minimal, romantic, emotional, nature and story.
- Background processing status and MP4 preview/download.
- Demucs + WhisperX + Puppeteer + FFmpeg pipeline.
- Headless rendering suitable for Codespaces/Linux.

The timeline on the current UI is an editor workspace preview, not yet a full drag-and-drop multitrack editor. Visual style presets currently influence the project metadata and drawing plan; each preset still needs its own complete art-direction library. Do not treat the application as production-ready until the real-song workflow and tests pass.

## Requirements
Python 3.10/3.11 recommended, Node.js 20+, FFmpeg and sufficient disk/RAM. CPU works but Demucs/WhisperX can be slow in small Codespaces. CUDA is optional.

## Run the web studio
```bash
bash run.sh
```
Open forwarded port 8000 in Codespaces. Upload a song and lyrics, choose a style and start rendering.

## Run pipeline directly
Place files at input/song.mp3 and input/lyrics.txt, then:
```bash
bash run.sh --render
```

## Configuration
Environment variables: LANGUAGE=en|hi, DEVICE=cpu|cuda|auto, FPS=30, WIDTH=1920, HEIGHT=1080, FFMPEG_PRESET=veryfast, FFMPEG_CRF=20.

## Alignment policy
Word timestamps come from forced alignment, not guessed distributions. If the model cannot align supplied words, inspect temp/timings.json and correct the lyrics or use a manual correction workflow. Language/model support varies.

## Important limitations
- First launch downloads large ML dependencies and model weights.
- A small Codespace may not have enough memory for long 1080p/30fps renders.
- The current web editor has a timeline overview; full interactive multitrack editing, scene authoring, per-style illustration packs, persistent project library and manual word-timing editor remain future implementation work.
- Test with a short, rights-cleared song before long renders.
