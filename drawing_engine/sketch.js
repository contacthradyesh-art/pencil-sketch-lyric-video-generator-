(()=>{const c=document.getElementById("paper"),x=c.getContext("2d");let plan={words:[],paths:[]};const paper=()=>{x.fillStyle="#f4ecd9";x.fillRect(0,0,1920,1080);for(let i=0;i<16000;i++){let a=Math.random()*0.035;x.fillStyle="rgba(90,70,40,"+a+")";x.fillRect(Math.random()*1920,Math.random()*1080,1,1)}};
function loadPlan(p){plan=p;window.__rendererReady=true}
function drawFrame(t){paper();x.strokeStyle="#333";x.lineWidth=2.5;x.lineCap="round";for(const p of plan.paths||[]){if(p.type==="line"){x.beginPath();x.moveTo(...p.points[0]);x.lineTo(...p.points[1]);x.stroke()}}
const shown=plan.words.filter(w=>Number(w.start)<=t);x.fillStyle="#24211d";x.font='54px "Caveat", "Comic Sans MS", cursive';x.textAlign="center";x.textBaseline="middle";let line="",start=0, row=0;
for(const w of shown){line+=(line?" ":"")+w.word;if(w.end>t)break;if(line.length>38){x.fillText(line,960,330+row*90);line="";row++}}
if(line)x.fillText(line,960,330+row*90);
}
window.PencilSketch={loadPlan,drawFrame};window.__rendererReady=false;paper()})();
