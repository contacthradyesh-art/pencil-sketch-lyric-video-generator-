#!/usr/bin/env python3
"""Run the complete audio-to-video pipeline from the repository root."""
import argparse, os, subprocess, sys, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args, label):
    print(f"\n[{label}] {' '.join(map(str,args))}",flush=True)
    subprocess.run(args,cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--keep-frames",action="store_true"); a=p.parse_args()
    audio=ROOT/"input/song.mp3"; lyrics=ROOT/"input/lyrics.txt"
    if not audio.is_file(): raise FileNotFoundError("Add input/song.mp3 before rendering.")
    if not lyrics.is_file() or not lyrics.read_text(encoding="utf-8-sig").strip(): raise FileNotFoundError("Add non-empty input/lyrics.txt before rendering.")
    py=sys.executable
    run([py,"src/separate_audio.py","--input",str(audio),"--device",os.getenv("DEVICE","cpu")],"demucs")
    run([py,"src/align_words.py","--language",os.getenv("LANGUAGE","en"),"--device",os.getenv("DEVICE","cpu")],"align")
    run([py,"src/build_drawing_plan.py","--style",os.getenv("STYLE","cinematic")],"drawing")
    run(["node","drawing_engine/render_frames.js"],"render")
    frames=ROOT/"temp/frames"; fps=os.getenv("FPS","30")
    out=ROOT/"output/final_video.mp4"; out.parent.mkdir(exist_ok=True)
    run(["ffmpeg","-y","-framerate",fps,"-start_number","1","-i",str(frames/"frame_%08d.png"),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-pix_fmt","yuv420p","-preset",os.getenv("FFMPEG_PRESET","veryfast"),"-crf",os.getenv("FFMPEG_CRF","20"),"-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(out)],"ffmpeg")
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(out)],capture_output=True,text=True,check=True)
    print(f"[success] Video created: {out} ({float(probe.stdout.strip()):.2f}s)",flush=True)
    if not a.keep_frames: shutil.rmtree(frames,ignore_errors=True)
if __name__=="__main__":
    try: main()
    except Exception as exc: print(f"[fatal] {exc}",file=sys.stderr); raise SystemExit(1)
