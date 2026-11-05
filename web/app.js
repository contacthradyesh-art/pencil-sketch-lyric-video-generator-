const $=s=>document.querySelector(s);let selectedStyle="cinematic",poller=null,timingData=null;
const audio=$("#audioPreview"),seek=$("#timelineSeek"),play=$("#playPreview");
const clock=n=>{if(!Number.isFinite(n))return "00:00";const m=Math.floor(n/60),s=Math.floor(n%60);return String(m).padStart(2,"0")+":"+String(s).padStart(2,"0")};
$("#song").addEventListener("change",e=>{const f=e.target.files[0];$("#songName").textContent=f?.name||"Choose your song";if(f){audio.src=URL.createObjectURL(f);audio.load();play.disabled=false;seek.disabled=false;$("#audioClip").textContent=f.name;}});
play.addEventListener("click",async()=>{if(audio.paused){try{await audio.play();play.textContent="Ⅱ";}catch(e){$("#error").textContent="Audio preview could not start: "+e.message;}}else{audio.pause();play.textContent="▶";}});
audio.addEventListener("loadedmetadata",()=>{$("#previewDuration").textContent=clock(audio.duration);seek.max=audio.duration||100;});
audio.addEventListener("timeupdate",()=>{seek.value=audio.currentTime;$("#previewTime").textContent=clock(audio.currentTime);});
audio.addEventListener("ended",()=>{play.textContent="▶";});
seek.addEventListener("input",()=>{if(Number.isFinite(audio.duration))audio.currentTime=Number(seek.value);});
document.querySelectorAll(".style").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".style").forEach(x=>x.classList.remove("selected"));b.classList.add("selected");selectedStyle=b.dataset.style;$("#style").value=selectedStyle;$(".paper").dataset.style=selectedStyle;}));
$("#createForm").addEventListener("submit",async e=>{e.preventDefault();const song=$("#song").files[0],lyrics=$("#lyrics").value.trim();if(!song||!lyrics){alert("Please select a song and enter lyrics.");return;}const fd=new FormData();fd.append("song",song);fd.append("lyrics",lyrics);fd.append("style",selectedStyle);fd.append("language",$("#language").value);fd.append("device",$("#device").value);fd.append("resolution",$("#resolution").value);fd.append("fps",$("#fps").value);const btn=$("#generate");btn.disabled=true;btn.querySelector("span").textContent="Uploading…";$("#error").textContent="";$("#result").hidden=true;try{const r=await fetch("/api/generate",{method:"POST",body:fd});const data=await r.json();if(!r.ok)throw new Error(data.detail||"Unable to start job");$("#jobTitle").textContent="Your video is in progress";poller=setInterval(refreshStatus,2500);await refreshStatus();}catch(err){$("#error").textContent=err.message;}finally{btn.disabled=false;btn.querySelector("span").textContent="Generate lyric video";}});
async function refreshStatus(){try{const r=await fetch("/api/status");const j=await r.json();$("#stage").textContent=j.stage||"Waiting";$("#percent").textContent=(j.progress||0)+"%";$("#progressBar").style.width=(j.progress||0)+"%";$("#jobMessage").textContent=j.message||"";$("#error").textContent=j.error||"";if(j.status==="completed"){clearInterval(poller);$("#jobTitle").textContent="Your video is ready";$("#result").hidden=false;$("#video").src="/api/video?t="+Date.now();if(!timingData)loadTimings();}if(j.status==="failed"){clearInterval(poller);$("#jobTitle").textContent="Rendering needs attention";}}catch(e){$("#error").textContent="Cannot read render status: "+e.message;}}

async function loadTimings(){
 try{
  const r=await fetch("/api/timings");if(!r.ok)throw new Error((await r.json()).detail||"Timing data not available");
  timingData=await r.json();const host=$("#timingRows");host.replaceChildren();
  timingData.words.forEach((w,i)=>{
   const row=document.createElement("div");row.className="timing-row";
   const word=document.createElement("b");word.className="timing-word";word.textContent=w.word;
   const start=document.createElement("input");start.type="number";start.min="0";start.step="0.01";start.value=Number(w.start).toFixed(2);start.dataset.index=i;start.dataset.field="start";start.setAttribute("aria-label","Start time for "+w.word);
   const end=document.createElement("input");end.type="number";end.min="0";end.step="0.01";end.value=Number(w.end).toFixed(2);end.dataset.index=i;end.dataset.field="end";end.setAttribute("aria-label","End time for "+w.word);
   const label=document.createElement("span");label.className="timing-index";label.textContent=String(i+1).padStart(3,"0");
   row.append(label,word,start,end);host.append(row);
  });
  $("#timingCount").textContent=timingData.words.length+" aligned words · edit seconds below";
  $("#timingEditor").hidden=false;
 }catch(e){$("#timingCount").textContent=e.message;}
}
$("#applyTimings").addEventListener("click",async()=>{
 if(!timingData)return;
 const btn=$("#applyTimings");btn.disabled=true;$("#error").textContent="";
 try{
  document.querySelectorAll(".timing-row input").forEach(input=>{const i=Number(input.dataset.index);timingData.words[i][input.dataset.field]=Number(input.value);});
  const r=await fetch("/api/timings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({words:timingData.words})});
  const data=await r.json();if(!r.ok)throw new Error(data.detail||"Could not save timing edits");
  $("#jobTitle").textContent="Applying timing corrections";$("#jobMessage").textContent=data.word_count+" word timings saved. Re-rendering the video.";
  timingData=null;if(poller)clearInterval(poller);poller=setInterval(refreshStatus,2500);await refreshStatus();
 }catch(e){$("#error").textContent=e.message;}finally{btn.disabled=false;}
});
