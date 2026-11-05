#!/usr/bin/env python3
"""Run and verify the complete audio-to-video pipeline."""
import json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(args,label):
    print(f"\n[{label}] {' '.join(map(str,args))}",flush=True)
    subprocess.run(args,cwd=ROOT,check=True)
def probe(path):
    result=subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],capture_output=True,text=True,check=True)
    return json.loads(result.stdout)
def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--keep-frames",action="store_true");a=p.parse_args()
    audio=ROOT/"input/song.mp3";lyrics=ROOT/"input/lyrics.txt"
    if not audio.is_file():raise FileNotFoundError("Add input/song.mp3 before rendering.")
    if not lyrics.is_file() or not lyrics.read_text(encoding="utf-8-sig").strip():raise FileNotFoundError("Add non-empty input/lyrics.txt before rendering.")
    py=sys.executable;device=os.getenv("DEVICE","cpu")
    run([py,"src/separate_audio.py","--input",str(audio),"--device",device],"demucs")
    run([py,"src/align_words.py","--language",os.getenv("LANGUAGE","en"),"--device",device],"align")
    run([py,"src/build_drawing_plan.py","--style",os.getenv("STYLE","cinematic")],"drawing")
    run(["node","drawing_engine/render_frames.js"],"render")
    frames=ROOT/"temp/frames";fps=os.getenv("FPS","30")
    first=frames/"frame_00000001.png"
    if not first.is_file():raise RuntimeError("The frame renderer finished without creating its first PNG frame.")
    out=ROOT/"output/final_video.mp4";out.parent.mkdir(exist_ok=True)
    run(["ffmpeg","-y","-framerate",fps,"-start_number","1","-i",str(frames/"frame_%08d.png"),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-pix_fmt","yuv420p","-preset",os.getenv("FFMPEG_PRESET","veryfast"),"-crf",os.getenv("FFMPEG_CRF","20"),"-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(out)],"ffmpeg")
    if not out.is_file() or out.stat().st_size<1024:raise RuntimeError("FFmpeg did not create a valid-sized MP4 file.")
    info=probe(out);types={stream.get("codec_type") for stream in info.get("streams",[])}
    if not {"video","audio"}.issubset(types):raise RuntimeError(f"Export is missing a video or audio stream: {sorted(types)}")
    duration=float(info.get("format",{}).get("duration",0))
    if duration<=0:raise RuntimeError("Exported MP4 has an invalid duration.")
    print(f"[success] Verified MP4: {out} | {duration:.2f}s | video + original audio streams present",flush=True)
    if not a.keep_frames:shutil.rmtree(frames,ignore_errors=True)
if __name__=="__main__":
    try:main()
    except Exception as exc:print(f"[fatal] {exc}",file=sys.stderr);raise SystemExit(1)
