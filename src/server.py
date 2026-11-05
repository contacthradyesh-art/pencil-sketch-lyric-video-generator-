#!/usr/bin/env python3
"""Local/Codespaces web app for Pencil Sketch Studio."""
from __future__ import annotations
import os, subprocess, sys, threading, uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

ROOT=Path(__file__).resolve().parents[1]
INPUT,OUTPUT,WEB=ROOT/"input",ROOT/"output",ROOT/"web"
for folder in (INPUT,OUTPUT,ROOT/"temp"): folder.mkdir(exist_ok=True)
app=FastAPI(title="Pencil Sketch Studio",version="1.1.0")
app.mount("/static",StaticFiles(directory=str(WEB)),name="static")
LOCK=threading.Lock()
JOB={"id":None,"status":"idle","stage":"Ready","progress":0,"message":"Upload a song and lyrics to begin.","error":None}
PROCESS=None

@app.get("/",response_class=HTMLResponse)
def home(): return (WEB/"index.html").read_text(encoding="utf-8")
@app.get("/api/health")
def health(): return {"ok":True,"app":"Pencil Sketch Studio","version":"1.1.0"}
@app.get("/api/status")
def status(): return dict(JOB)
@app.get("/api/video")
def video():
    p=OUTPUT/"final_video.mp4"
    if not p.exists(): raise HTTPException(404,"No rendered video yet.")
    return FileResponse(p,media_type="video/mp4",filename="pencil-sketch-lyrics.mp4")

def run_pipeline(style,language,device,width,height,fps):
    global PROCESS
    try:
        JOB.update(status="running",stage="Audio separation",progress=3,message="Starting audio separation…",error=None)
        env=os.environ.copy(); env.update({"STYLE":style,"LANGUAGE":language,"DEVICE":device,"WIDTH":str(width),"HEIGHT":str(height),"FPS":str(fps)})
        PROCESS=subprocess.Popen([sys.executable,"src/main.py"],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        stage_map=[("demucs","Audio separation",12),("align","Word alignment",35),("drawing","Drawing plan",52),("render","Pencil animation rendering",65),("ffmpeg","Final video encoding",90)]
        assert PROCESS.stdout is not None
        for line in PROCESS.stdout:
            msg=line.strip()
            if not msg: continue
            low=msg.lower()
            for token,stage,pct in stage_map:
                if token in low: JOB.update(stage=stage,progress=max(JOB["progress"],pct))
            JOB["message"]=msg[-500:]
        code=PROCESS.wait()
        if code: raise RuntimeError(f"Pipeline exited with code {code}. {JOB.get('message','')}")
        JOB.update(status="completed",stage="Complete",progress=100,message="Video ready to preview and download.",error=None)
    except Exception as exc:
        JOB.update(status="failed",stage="Failed",message="Video generation failed.",error=str(exc))
    finally: PROCESS=None

@app.post("/api/generate")
async def generate(song:UploadFile=File(...),lyrics:str=Form(...),style:str=Form("cinematic"),language:str=Form("en"),device:str=Form("cpu"),resolution:str=Form("1080p"),fps:int=Form(30)):
    if not song.filename or Path(song.filename).suffix.lower() not in {".mp3",".wav",".m4a"}:
        raise HTTPException(400,"Upload an MP3, WAV or M4A audio file.")
    if not lyrics.strip(): raise HTTPException(400,"Lyrics cannot be empty.")
    allowed={"cinematic","minimal","romantic","emotional","nature","story","custom"}
    if style not in allowed: raise HTTPException(400,"Unknown visual style.")
    if language not in {"en","hi"}: raise HTTPException(400,"Language must be en or hi.")
    if device not in {"cpu","cuda","auto"}: raise HTTPException(400,"Invalid compute device.")\n    if resolution not in {"720p","1080p"}: raise HTTPException(400,"Resolution must be 720p or 1080p.")\n    if fps not in {30,60}: raise HTTPException(400,"FPS must be 30 or 60.")
    async with _async_lock:
        with LOCK:
            if JOB["status"] in {"queued","running"}: raise HTTPException(409,"A render is already running.")
        data=await song.read()
        if not data: raise HTTPException(400,"Uploaded audio file is empty.")
        if len(data)>200*1024*1024: raise HTTPException(413,"Audio file exceeds 200 MB.")
        suffix=Path(song.filename).suffix.lower()
        source=ROOT/"temp"/("upload"+suffix)
        source.write_bytes(data)
        target=INPUT/"song.mp3"
        try:
            subprocess.run(["ffmpeg","-y","-i",str(source),"-vn","-codec:a","libmp3lame","-q:a","2",str(target)],check=True,capture_output=True)
        except FileNotFoundError: raise HTTPException(500,"FFmpeg is missing. Install FFmpeg and restart the app.")
        except subprocess.CalledProcessError as exc: raise HTTPException(400,"Could not decode the uploaded audio. "+exc.stderr.decode(errors="ignore")[-400:])
        (INPUT/"lyrics.txt").write_text(lyrics.strip()+"\n",encoding="utf-8")
        with LOCK:
            JOB.update(id=str(uuid.uuid4()),status="queued",stage="Queued",progress=0,message="Project queued.",error=None)
            width,height=(1280,720) if resolution=="720p" else (1920,1080)\n            threading.Thread(target=run_pipeline,args=(style,language,device,width,height,fps),daemon=True).start()
        return {"job_id":JOB["id"],"status":"queued"}

import asyncio
_async_lock=asyncio.Lock()

if __name__=="__main__":
    import uvicorn
    uvicorn.run("src.server:app",host=os.getenv("HOST","0.0.0.0"),port=int(os.getenv("PORT","8000")),reload=False)
