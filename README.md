# Pencil Sketch Studio AI

A browser-based creative studio for generating hand-drawn pencil-sketch lyric videos from an uploaded song and user-supplied lyrics.

## What is implemented

- Responsive dark studio dashboard.
- MP3/WAV/M4A upload and in-browser audio preview with play/pause and timeline seeking.
- Lyrics input, English/Hindi language selection and six visual style presets.
- 720p/1080p and 30/60 FPS render settings.
- FastAPI upload API, background render job and progress/status endpoints.
- Demucs vocal separation, WhisperX forced word alignment and validation (no guessed word timings).
- Style-aware Canvas drawing scenes, paper grain and word-by-word lyric reveal.
- Puppeteer frame rendering and FFmpeg MP4 export with the uploaded original audio.
- MP4 preview/download after successful render.
- GitHub Actions syntax/unit checks and Codespaces setup.

## Run in GitHub Codespaces

Open the repository in Codespaces. The devcontainer installs FFmpeg and Devanagari fonts. Then run:

```bash
bash run.sh
```

Open forwarded port 8000. First-time setup downloads large Python/ML packages and model weights.

## Run locally

Requirements: Python 3.11, Node.js 20+, FFmpeg/ffprobe.

```bash
bash run.sh
```

## Render from the command line

Put a song at `input/song.mp3` and matching lyrics at `input/lyrics.txt`, then:

```bash
bash run.sh --render
```

## Settings

The web form supports:
- Language: English or Hindi.
- Style: cinematic, minimal, romantic, emotional, nature or story.
- Resolution: 720p or 1080p.
- Frame rate: 30 or 60 FPS.
- Processing: CPU, auto-detect or CUDA.

## Important notes and current limitations

- Forced alignment quality depends on the language, audio clarity, lyrics accuracy and WhisperX alignment-model support. The pipeline intentionally fails when word alignment coverage is too low instead of fabricating timestamps.
- CPU-only Codespaces can take a long time and may run out of RAM/disk for long tracks or 1080p/60 FPS. Start with a short sample and 720p/30 FPS.
- The current timeline provides audio preview and seeking plus a visual track overview. It is not yet a full multitrack drag-and-drop editor.
- Manual per-word timing correction, scene/image uploads, persistent project library, per-scene keyframes, and advanced transition/effect controls are not implemented yet.
- The visual presets use generated Canvas pencil strokes and motifs. They are not yet a semantic AI illustration system that understands each lyric and invents a unique storyboard for every line.
- Test the complete pipeline with a short, rights-cleared song before relying on longer renders.
