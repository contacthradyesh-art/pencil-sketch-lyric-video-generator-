#!/usr/bin/env python3
"""Local/Codespaces web app for Pencil Sketch Studio."""
from __future__ import annotations
import json, os, subprocess, sys, threading, uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from src.validators import validate_word_timings
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
PROJECT_SETTINGS={"style":"cinematic","width":1920,"height":1080,"fps":30}

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


def run_export():
    global PROCESS
    try:
        JOB.update(status="running",stage="Rebuilding drawing plan",progress=10,message="Applying your corrected word timings…",error=None)
        env=os.environ.copy();env.update({"STYLE":PROJECT_SETTINGS["style"],"WIDTH":str(PROJECT_SETTINGS["width"]),"HEIGHT":str(PROJECT_SETTINGS["height"]),"FPS":str(PROJECT_SETTINGS["fps"])})
        PROCESS=subprocess.Popen([sys.executable,"src/export_video.py"],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        for line in PROCESS.stdout or []:
            msg=line.strip()
            if not msg:continue
            low=msg.lower()
            if "drawing" in low:JOB.update(stage="Drawing plan",progress=20)
            elif "render" in low:JOB.update(stage="Pencil animation rendering",progress=35)
            elif "ffmpeg" in low:JOB.update(stage="Final video encoding",progress=85)
            JOB["message"]=msg[-500:]
        code=PROCESS.wait()
        if code:raise RuntimeError(f"Re-export failed with code {code}: {JOB.get('message','')}")
        JOB.update(status="completed",stage="Complete",progress=100,message="Updated video ready to preview and download.",error=None)
    except Exception as exc:JOB.update(status="failed",stage="Failed",message="Re-export failed.",error=str(exc))
    finally:PROCESS=None

@app.get("/api/timings")
def get_timings():
    p=ROOT/"temp/timings.json"
    if not p.is_file():raise HTTPException(404,"Word timings are not available until the first render reaches alignment.")
    return json.loads(p.read_text(encoding="utf-8"))

@app.post("/api/timings")
async def save_timings(request:Request):
    payload=await request.json()
    words=payload.get("words") if isinstance(payload,dict) else None
    if not isinstance(words,list):raise HTTPException(400,"A words array is required.")
    current=ROOT/"temp/timings.json"
    if not current.is_file():raise HTTPException(409,"Generate a video first so aligned timings exist.")
    original=json.loads(current.read_text(encoding="utf-8"))
    try:coverage=validate_word_timings(words,original.get("expected_words",len(words)),.98)
    except ValueError as exc:raise HTTPException(422,str(exc))
    original["words"]=words;original["aligned_words"]=len(words);original["coverage"]=coverage;original["manual_edits"]=True
    temp=current.with_suffix(".json.tmp");temp.write_text(json.dumps(original,ensure_ascii=False,indent=2),encoding="utf-8");temp.replace(current)
    with LOCK:
        if JOB["status"] in {"queued","running"}:raise HTTPException(409,"Wait for the current render to finish.")
        (OUTPUT/"final_video.mp4").unlink(missing_ok=True)
        JOB.update(id=str(uuid.uuid4()),status="queued",stage="Queued",progress=0,message="Manual timing edits saved; re-render queued.",error=None)
        threading.Thread(target=run_export,daemon=True).start()
    return {"saved":True,"word_count":len(words),"status":"queued"}

@app.post("/api/generate")
async def generate(song:UploadFile=File(...),lyrics:str=Form(...),style:str=Form("cinematic"),language:str=Form("en"),device:str=Form("cpu"),resolution:str=Form("1080p"),fps:int=Form(30)):
    if not song.filename or Path(song.filename).suffix.lower() not in {".mp3",".wav",".m4a"}:
        raise HTTPException(400,"Upload an MP3, WAV or M4A audio file.")
    if not lyrics.strip(): raise HTTPException(400,"Lyrics cannot be empty.")
    allowed={"cinematic","minimal","romantic","emotional","nature","story","custom"}
    if style not in allowed: raise HTTPException(400,"Unknown visual style.")
    if language not in {"en","hi"}: raise HTTPException(400,"Language must be en or hi.")
    if device not in {"cpu","cuda","auto"}: raise HTTPException(400,"Invalid compute device.")
    if resolution not in {"720p","1080p"}: raise HTTPException(400,"Resolution must be 720p or 1080p.")
    if fps not in {30,60}: raise HTTPException(400,"FPS must be 30 or 60.")
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
        (OUTPUT/"final_video.mp4").unlink(missing_ok=True)
        try:
            subprocess.run(["ffmpeg","-y","-i",str(source),"-vn","-codec:a","libmp3lame","-q:a","2",str(target)],check=True,capture_output=True)
        except FileNotFoundError: raise HTTPException(500,"FFmpeg is missing. Install FFmpeg and restart the app.")
        except subprocess.CalledProcessError as exc: raise HTTPException(400,"Could not decode the uploaded audio. "+exc.stderr.decode(errors="ignore")[-400:])
        (INPUT/"lyrics.txt").write_text(lyrics.strip()+"\n",encoding="utf-8")
        PROJECT_SETTINGS.update({"style":style,"width":1280 if resolution=="720p" else 1920,"height":720 if resolution=="720p" else 1080,"fps":fps})
        with LOCK:
            JOB.update(id=str(uuid.uuid4()),status="queued",stage="Queued",progress=0,message="Project queued.",error=None)
            width,height=(1280,720) if resolution=="720p" else (1920,1080)
            threading.Thread(target=run_pipeline,args=(style,language,device,width,height,fps),daemon=True).start()
        return {"job_id":JOB["id"],"status":"queued"}

import asyncio
_async_lock=asyncio.Lock()

if __name__=="__main__":
    import uvicorn
    uvicorn.run("src.server:app",host=os.getenv("HOST","0.0.0.0"),port=int(os.getenv("PORT","8000")),reload=False)
