#!/usr/bin/env python3
"""Build a deterministic, style-aware pencil drawing plan from aligned words."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STYLES={"cinematic":"graphite","minimal":"minimal","romantic":"romantic","emotional":"emotional","nature":"nature","story":"story","custom":"graphite"}
def audio_duration(path):
    try:
        r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
        return float(r.stdout.strip())
    except Exception:return 0.0
def path(points,start,duration,width=2.5):return {"type":"path","points":points,"start":start,"duration":duration,"width":width}
def style_paths(style,duration):
    base=[path([[70,820],[190,700],[310,770],[440,570],[570,760],[710,650],[840,800]],0,min(12,max(4,duration*.25)),3),
          path([[900,810],[1040,620],[1160,710],[1300,510],[1460,735],[1610,625],[1840,810]],duration*.18,min(15,max(5,duration*.3)),2.5),
          path([[0,855],[300,830],[600,855],[900,830],[1200,855],[1500,830],[1920,850]],duration*.35,min(10,max(4,duration*.2)),1.8)]
    if style=="minimal":return [path([[220,760],[500,760],[800,760],[1120,760],[1450,760],[1700,760]],0,max(4,duration*.35),1.8)]
    if style=="romantic":
        base += [path([[1450,280],[1410,235],[1360,245],[1340,290],[1400,350],[1460,410],[1520,350],[1580,290],[1560,245],[1510,235],[1460,280]],duration*.28,max(5,duration*.18),2.8),
                 path([[260,700],[230,650],[250,600],[290,575],[330,600],[350,650],[320,700]],duration*.52,max(4,duration*.16),2)]
    elif style=="emotional":
        for i in range(13):
            x=100+i*140
            base.append(path([[x,130],[x-20,220],[x-35,290]],duration*.2+(i%4)*.4,max(4,duration*.35),1.1))
        base.append(path([[700,700],[770,650],[840,700],[910,650],[980,700]],duration*.6,max(4,duration*.18),2))
    elif style=="nature":
        base += [path([[260,820],[260,640],[250,520],[210,450]],duration*.22,max(5,duration*.2),4),
                 path([[260,620],[330,520],[400,510],[350,600],[260,620]],duration*.32,max(5,duration*.2),2),
                 path([[260,650],[190,560],[120,560],[170,640],[260,650]],duration*.42,max(5,duration*.2),2)]
    elif style=="story":
        base += [path([[780,790],[780,610],[820,540],[860,610],[860,790]],duration*.22,max(5,duration*.2),2.8),
                 path([[810,550],[770,480],[810,430],[850,480],[810,550]],duration*.32,max(5,duration*.2),2.4),
                 path([[1120,800],[1120,650],[1160,590],[1200,650],[1200,800]],duration*.5,max(5,duration*.2),2.5)]
    return base
def main():
    p=argparse.ArgumentParser();p.add_argument("--timings",type=Path,default=ROOT/"temp/timings.json");p.add_argument("--output",type=Path,default=ROOT/"temp/drawing_plan.json");p.add_argument("--style",choices=STYLES,default="cinematic");a=p.parse_args()
    data=json.loads(a.timings.read_text(encoding="utf-8"));words=data.get("words",[])
    if not words:raise SystemExit("No aligned words available; refusing to invent timings.")
    end=max(float(w["end"]) for w in words);duration=max(end,audio_duration(ROOT/"input/song.mp3"))
    plan={"version":1,"style":a.style,"visual_style":STYLES[a.style],"duration":duration,"words":words,"paths":style_paths(a.style,duration),"canvas":{"width":1920,"height":1080},"text":{"x":160,"y":370,"max_width":1600,"font_size":62}}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"[drawing] Plan created: style={a.style}, paths={len(plan['paths'])}, words={len(words)}, duration={duration:.2f}s")
if __name__=="__main__":main()
