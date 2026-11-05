#!/usr/bin/env python3
"""Build a deterministic, style-aware pencil drawing plan from aligned words."""
import argparse,json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STYLES={"cinematic":"graphite","minimal":"minimal","romantic":"romantic","emotional":"emotional","nature":"nature","story":"story","custom":"graphite"}
def audio_duration(path):
    try:
        r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
        return float(r.stdout.strip())
    except Exception: return 0.0
def main():
    p=argparse.ArgumentParser(); p.add_argument("--timings",type=Path,default=ROOT/"temp/timings.json"); p.add_argument("--output",type=Path,default=ROOT/"temp/drawing_plan.json"); p.add_argument("--style",choices=STYLES,default="cinematic"); a=p.parse_args()
    data=json.loads(a.timings.read_text(encoding="utf-8")); words=data.get("words",[])
    if not words: raise SystemExit("No aligned words available; refusing to invent timings.")
    end=max(float(w["end"]) for w in words); duration=max(end,audio_duration(ROOT/"input/song.mp3"))
    # Normalized hand-drawn landscape scene; paths reveal progressively during the song.
    paths=[
      {"type":"path","points":[[80,810],[180,690],[280,760],[410,560],[550,750],[690,650],[820,790]],"start":0.0,"duration":min(12,max(4,duration*.25)),"width":3.0},
      {"type":"path","points":[[900,800],[1040,610],[1160,710],[1300,500],[1460,730],[1610,620],[1810,800]],"start":max(0,duration*.18),"duration":min(15,max(5,duration*.3)),"width":2.5},
      {"type":"path","points":[[0,850],[300,830],[600,855],[900,825],[1200,850],[1500,820],[1920,845]],"start":max(0,duration*.35),"duration":min(10,max(4,duration*.2)),"width":1.8},
      {"type":"path","points":[[1550,170],[1550,240],[1550,310],[1550,380]],"start":max(0,duration*.45),"duration":min(8,max(3,duration*.12)),"width":2}
    ]
    plan={"version":1,"style":a.style,"visual_style":STYLES[a.style],"duration":duration,"words":words,"paths":paths,"canvas":{"width":1920,"height":1080},"text":{"x":960,"y":390,"max_width":1500,"font_size":62}}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"[drawing] Plan created: style={a.style}, words={len(words)}, duration={duration:.2f}s")
if __name__=="__main__": main()
