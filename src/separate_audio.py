#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=ROOT/"input/song.mp3")
    p.add_argument("--temp",type=Path,default=ROOT/"temp")
    p.add_argument("--model",default="htdemucs")
    p.add_argument("--device",default="cpu",choices=["cpu","cuda","auto"])
    a=p.parse_args(); src=a.input.resolve(); tmp=a.temp.resolve()
    if not src.is_file(): p.error(f"Missing audio: {src}")
    tmp.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,"-m","demucs","--two-stems=vocals","-n",a.model,"-o",str(tmp/"demucs")]
    if a.device!="auto": cmd += ["-d",a.device]
    cmd.append(str(src)); print("[demucs] Separating audio...",flush=True)
    subprocess.run(cmd,check=True)
    track=tmp/"demucs"/a.model/src.stem
    for name in ("vocals.wav","no_vocals.wav"):
        found=track/name
        if not found.exists(): raise FileNotFoundError(found)
        shutil.copy2(found,tmp/name)
        print(f"[ok] {tmp/name}")
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"[error] {e}",file=sys.stderr); raise SystemExit(1)
