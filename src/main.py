#!/usr/bin/env python3
import argparse,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args): print("\n[run]"," ".join(map(str,args)),flush=True); subprocess.run(args,cwd=ROOT,check=True)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--keep-frames",action="store_true"); a=p.parse_args()
 py=sys.executable
 run([py,"src/separate_audio.py"])
 run([py,"src/align_words.py","--language",os.getenv("LANGUAGE","en"),"--device",os.getenv("DEVICE","cpu")])
 run([py,"src/build_drawing_plan.py"])
 env=os.environ.copy()
 cmd=["node","drawing_engine/render_frames.js"]
 run(cmd)
 frames=ROOT/"temp/frames"
 run(["ffmpeg","-y","-framerate",os.getenv("FPS","30"),"-i",str(frames/"frame_%08d.png"),"-i",str(ROOT/"input/song.mp3"),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-pix_fmt","yuv420p","-preset",os.getenv("FFMPEG_PRESET","medium"),"-crf",os.getenv("FFMPEG_CRF","18"),"-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(ROOT/"output/final_video.mp4")])
 if not a.keep_frames: import shutil; shutil.rmtree(frames,ignore_errors=True)
 print("[success] output/final_video.mp4")
if __name__=="__main__":
 try: main()
 except subprocess.CalledProcessError as e: raise SystemExit(e.returncode or 1)
