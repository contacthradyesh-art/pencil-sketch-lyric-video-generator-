(()=> {
 "use strict";
 const canvas=document.getElementById("paper"),ctx=canvas.getContext("2d"),W=1920,H=1080;
 let plan={words:[],paths:[],style:"cinematic"},paper=document.createElement("canvas"),pg=paper.getContext("2d");
 paper.width=W;paper.height=H;let seed=82431;
 const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
 pg.fillStyle="#f0e7d7";pg.fillRect(0,0,W,H);
 for(let i=0;i<32000;i++){const a=.018+rand()*.045;pg.fillStyle=rand()>.5?"rgba(73,59,43,"+a+")":"rgba(255,255,255,"+a+")";pg.fillRect(rand()*W,rand()*H,.7+rand()*1.7)}
 function palette(){const s=plan.style;return s==="romantic"?["#59434b","#a77e88","#d3a9a9"]:s==="emotional"?["#34343a","#77727b","#aaa0a0"]:s==="nature"?["#394d40","#74816b","#a2a58b"]:s==="minimal"?["#514b42","#a69b88","#c9bca8"]:["#38332d","#777064","#aaa08e"]}
 function stroke(points,t,start,duration,width=2,alpha=.86,color=null){
  if(points.length<2)return;const p=Math.max(0,Math.min(1,(t-start)/Math.max(.01,duration)));if(!p)return;
  let lens=[],total=0;for(let i=1;i<points.length;i++){const d=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lens.push(d);total+=d}
  let left=total*p;ctx.beginPath();ctx.moveTo(points[0][0],points[0][1]);
  for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],d=lens[i-1];if(left>=d){ctx.lineTo(b[0],b[1]);left-=d}else{const q=left/d;ctx.lineTo(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);break}}
  const colors=palette();ctx.strokeStyle=color||colors[0];ctx.lineWidth=width;ctx.lineCap="round";ctx.lineJoin="round";ctx.globalAlpha=alpha;ctx.stroke();ctx.globalAlpha=1;
 }
 function sketchScene(t){
  const colors=palette(),ink=colors[0],soft=colors[1],style=plan.style,d=Math.max(1,plan.duration||60);
  if(style!=="minimal"){
   stroke([[0,790],[160,710],[310,770],[490,640],[660,760],[850,700],[1030,770],[1210,660],[1400,750],[1590,690],[1780,770],[1920,730]],t,0,d*.18,3);
   stroke([[0,850],[240,820],[470,850],[720,815],[960,850],[1200,820],[1450,850],[1700,820],[1920,850]],t,d*.1,d*.2,1.8,.6,soft);
   for(let i=0;i<16;i++){const x=80+i*115,y=820+(i%3)*9;stroke([[x,y],[x+25,y-18],[x+50,y]],t,d*.2+i*.08,d*.25,1,.28,soft)}
  }
  const sunStart=d*.05,sunProgress=Math.max(0,Math.min(1,(t-sunStart)/(d*.15)));
  if(sunProgress>0){ctx.save();ctx.translate(1530,270);ctx.strokeStyle=ink;ctx.lineWidth=2;ctx.globalAlpha=.72;ctx.beginPath();ctx.arc(0,0,78,0,Math.PI*2*sunProgress);ctx.stroke();if(sunProgress>.9){ctx.globalAlpha=.28;ctx.beginPath();ctx.arc(3,2,83,0,Math.PI*2);ctx.stroke()}ctx.restore()}
  if(style==="romantic"){
   stroke([[380,370],[330,325],[275,335],[255,395],[310,455],[380,520],[450,455],[505,395],[485,335],[430,325],[380,370]],t,d*.22,d*.16,4);
   for(let i=0;i<5;i++){const x=200+i*340;stroke([[x,800],[x-20,740],[x+10,680],[x+55,650],[x+75,690],[x+40,740],[x,800]],t,d*.35+i*.5,d*.2,1.6,.65,soft)}
  }else if(style==="nature"){
   stroke([[260,835],[260,610],[255,500],[220,420]],t,d*.16,d*.22,5);
   stroke([[260,650],[320,560],[410,545],[355,630],[260,650]],t,d*.23,d*.18,2.8);
   stroke([[260,690],[190,595],[105,590],[160,680],[260,690]],t,d*.31,d*.18,2.8);
   stroke([[1650,820],[1650,620],[1590,560],[1515,560],[1585,640],[1650,665],[1720,570],[1800,570],[1730,655],[1650,690]],t,d*.4,d*.25,3);
  }else if(style==="story"){
   stroke([[900,820],[900,610],[930,555],[960,610],[960,820]],t,d*.2,d*.2,3);
   stroke([[930,555],[885,500],[930,440],[975,500],[930,555]],t,d*.28,d*.18,3);
   stroke([[1200,820],[1200,670],[1240,620],[1280,670],[1280,820]],t,d*.48,d*.2,3);
   stroke([[1130,820],[1130,740],[1350,740],[1350,820]],t,d*.55,d*.15,2);
  }else if(style==="emotional"){
   for(let i=0;i<14;i++){const x=90+i*135;stroke([[x,120],[x-18,190],[x-30,265]],t,d*.25+(i%5)*.24,d*.3,1.1,.45,soft)}
   stroke([[600,810],[690,750],[780,810],[870,750],[960,810],[1050,750],[1140,810]],t,d*.5,d*.2,2.3,.65);
  }else if(style==="cinematic"){
   stroke([[360,810],[360,650],[395,580],[430,650],[430,810]],t,d*.2,d*.2,3);
   stroke([[395,580],[350,520],[395,460],[440,520],[395,580]],t,d*.28,d*.16,2.4);
   stroke([[1430,810],[1430,650],[1470,580],[1510,650],[1510,810]],t,d*.4,d*.2,3);
  }
  if(style!=="minimal"){ctx.strokeStyle=soft;ctx.globalAlpha=.18;ctx.lineWidth=1;ctx.strokeRect(30,30,W-60,H-60);ctx.globalAlpha=1}
 }
 function drawLyrics(t){
  const words=plan.words||[];if(!words.length)return;
  const active=words.findIndex(w=>t>=Number(w.start)&&t<=Number(w.end));
  let activeLine=active>=0?(words[active].line_index??0):(words.find(w=>Number(w.start)>t)?.line_index??words[words.length-1].line_index??0);
  const groups=new Map();for(const w of words){const k=w.line_index??0;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(w)}
  const lines=[...groups.keys()].sort((a,b)=>a-b),pos=lines.indexOf(activeLine),visibleLines=lines.slice(Math.max(0,pos-1),Math.min(lines.length,pos+2));
  const fontSize=Number(plan.text?.font_size||60),lineHeight=fontSize*1.48;
  ctx.textBaseline="middle";ctx.textAlign="left";ctx.font=fontSize+'px "Noto Sans Devanagari","Nirmala UI","Mangal","Caveat","Comic Sans MS",cursive';
  const baseY=390-(visibleLines.length-1)*lineHeight/2;
  visibleLines.forEach((lineId,row)=>{
   const lineWords=groups.get(lineId),full=lineWords.map(w=>String(w.word).trim()).join(" "),measure=ctx.measureText(full).width;
   let x=Math.max(100,(W-measure)/2),y=baseY+row*lineHeight;
   const current=lineId===activeLine;
   for(const w of lineWords){
    const start=Number(w.start),end=Number(w.end);if(t<start)break;
    const word=String(w.word).trim(),ratio=Math.max(0,Math.min(1,(t-start)/Math.max(.04,end-start)));
    if(ratio<=0)break;
    const shown=ratio>=1?word:word.slice(0,Math.max(1,Math.ceil(word.length*ratio)));
    ctx.fillStyle=current?"#29251f":"#827a6e";ctx.globalAlpha=current?1:.43;ctx.fillText(shown,x,y);ctx.globalAlpha=1;
    const width=ctx.measureText(word+" ").width;
    if(ratio<1){ctx.strokeStyle="#9a7b67";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x,y+fontSize*.62);ctx.lineTo(x+Math.max(4,width*ratio),y+fontSize*.62);ctx.stroke();break}
    x+=width;
   }
  });
 }
 function drawFrame(t){ctx.drawImage(paper,0,0);sketchScene(t);for(const p of plan.paths||[])stroke(p.points,t,Number(p.start||0),Number(p.duration||5),Number(p.width||2.5));drawLyrics(t)}
 function loadPlan(p){plan=p;window.__rendererReady=true}
 window.PencilSketch={loadPlan,drawFrame};window.__rendererReady=false;ctx.drawImage(paper,0,0);
})();