#!/usr/bin/env python3
"""Rebuild a video from saved word timings without repeating audio separation."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(cmd,label):print(f"\n[{label}] {' '.join(map(str,cmd))}",flush=True);subprocess.run(cmd,cwd=ROOT,check=True)
def main():
 p=argparse.ArgumentParser();p.add_argument("--style",default=os.getenv("STYLE","cinematic"));p.add_argument("--width",type=int,default=int(os.getenv("WIDTH","1920")));p.add_argument("--height",type=int,default=int(os.getenv("HEIGHT","1080")));p.add_argument("--fps",type=int,default=int(os.getenv("FPS","30")));a=p.parse_args()
 audio=ROOT/"input/song.mp3";timings=ROOT/"temp/timings.json"
 if not audio.is_file() or not timings.is_file():raise FileNotFoundError("Original song and aligned timings must exist before re-export.")
 run([sys.executable,"src/build_drawing_plan.py","--timings",str(timings),"--style",a.style],"drawing")
 run(["node","drawing_engine/render_frames.js"],"render")
 frames=ROOT/"temp/frames";first=frames/"frame_00000001.png"
 if not first.is_file():raise RuntimeError("Renderer produced no frames.")
 out=ROOT/"output/final_video.mp4"
 run(["ffmpeg","-y","-framerate",str(a.fps),"-start_number","1","-i",str(frames/"frame_%08d.png"),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-pix_fmt","yuv420p","-preset",os.getenv("FFMPEG_PRESET","veryfast"),"-crf",os.getenv("FFMPEG_CRF","20"),"-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(out)],"ffmpeg")
 info=json.loads(subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(out)],capture_output=True,text=True,check=True).stdout)
 types={x.get("codec_type") for x in info.get("streams",[])}
 if not {"video","audio"}.issubset(types):raise RuntimeError("Export must contain both video and audio streams.")
 print("[success] Corrected-timing MP4 exported and verified.",flush=True)
if __name__=="__main__":
 try:main()
 except Exception as exc:print(f"[fatal] {exc}",file=sys.stderr);raise SystemExit(1)
