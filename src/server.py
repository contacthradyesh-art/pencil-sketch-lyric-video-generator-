#!/usr/bin/env python3
"""Local/Codespaces web app for creating pencil-sketch lyric videos."""
from __future__ import annotations
import os, subprocess, sys, threading, uuid
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
INPUT, OUTPUT, WEB = ROOT/"input", ROOT/"output", ROOT/"web"
INPUT.mkdir(exist_ok=True); OUTPUT.mkdir(exist_ok=True)
app = FastAPI(title="Pencil Sketch Studio", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(WEB)), name="static")
LOCK = threading.Lock()
JOB = {"id": None, "status": "idle", "stage": "Ready", "progress": 0, "message": "Upload a song and lyrics to begin.", "error": None}
PROCESS: Optional[subprocess.Popen] = None

@app.get("/", response_class=HTMLResponse)
def home():
    return (WEB/"index.html").read_text(encoding="utf-8")

@app.get("/api/status")
def status():
    return dict(JOB)

@app.get("/api/video")
def video():
    p=OUTPUT/"final_video.mp4"
    if not p.exists(): raise HTTPException(404,"No rendered video yet.")
    return FileResponse(p, media_type="video/mp4", filename="pencil-sketch-lyrics.mp4")

def _run_job(style: str, language: str, device: str):
    global PROCESS
    try:
        JOB.update(status="running",stage="Audio separation",progress=5,message="Starting Demucs…",error=None)
        env=os.environ.copy(); env.update({"STYLE":style,"LANGUAGE":language,"DEVICE":device})
        PROCESS=subprocess.Popen([sys.executable,"src/main.py"],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        stages={"demucs":("Audio separation",10),"align":("Word alignment",35),"drawing":("Drawing plan",55),"node":("Pencil animation rendering",65),"ffmpeg":("Video encoding",90)}
        assert PROCESS.stdout is not None
        for line in PROCESS.stdout:
            msg=line.strip()
            low=msg.lower()
            for key,(stage,progress) in stages.items():
                if key in low or stage.lower() in low:
                    JOB.update(stage=stage,progress=progress)
            if msg: JOB["message"]=msg[-500:]
        code=PROCESS.wait()
        if code: raise RuntimeError(f"Pipeline exited with code {code}. Last output: {JOB.get('message')}")
        JOB.update(status="completed",stage="Complete",progress=100,message="Video ready to preview and download.",error=None)
    except Exception as exc:
        JOB.update(status="failed",stage="Failed",message="Video generation failed.",error=str(exc))
    finally:
        PROCESS=None

@app.post("/api/generate")
async def generate(song: UploadFile=File(...), lyrics: str=Form(...), style: str=Form("cinematic"), language: str=Form("en"), device: str=Form("cpu")):
    if not song.filename or Path(song.filename).suffix.lower() not in {".mp3",".wav",".m4a"}:
        raise HTTPException(400,"Upload an MP3, WAV or M4A audio file.")
    if not lyrics.strip(): raise HTTPException(400,"Lyrics cannot be empty.")
    if style not in {"cinematic","minimal","romantic","emotional","nature","story","custom"}:
        raise HTTPException(400,"Unknown visual style.")
    if language not in {"en","hi"}: raise HTTPException(400,"Language must be en or hi.")
    if device not in {"cpu","cuda","auto"}: raise HTTPException(400,"Invalid compute device.")
    with LOCK:
        if JOB["status"]=="running": raise HTTPException(409,"A render is already running.")
        suffix=Path(song.filename).suffix.lower()
        data=await song.read()
        if len(data)>200*1024*1024: raise HTTPException(413,"Audio file exceeds 200 MB.")
        (INPUT/f"song{suffix}").write_bytes(data)
        # Pipeline expects song.mp3; keep extension-independent canonical path.
        canonical=INPUT/"song.mp3"
        if suffix!=".mp3":
            converted=ROOT/"temp"/"uploaded-audio.wav"
            converted.parent.mkdir(exist_ok=True)
            subprocess.run(["ffmpeg","-y","-i",str(INPUT/f"song{suffix}"),str(converted)],check=True,capture_output=True)
            canonical=converted
        (INPUT/"lyrics.txt").write_text(lyrics.strip()+"\n",encoding="utf-8")
        # Audio separation accepts this explicit input through AUDIO_INPUT.
        JOB.update(id=str(uuid.uuid4()),status="queued",stage="Queued",progress=0,message="Job queued.",error=None)
        thread=threading.Thread(target=_run_job,args=(style,language,device),daemon=True); thread.start()
    return {"job_id":JOB["id"],"status":"queued"}

@app.get("/api/health")
def health(): return {"ok":True,"app":"Pencil Sketch Studio","version":"1.0.0"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("src.server:app",host=os.getenv("HOST","0.0.0.0"),port=int(os.getenv("PORT","8000")),reload=False)
