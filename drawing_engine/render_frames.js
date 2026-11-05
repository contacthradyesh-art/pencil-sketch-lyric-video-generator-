const fs=require("fs-extra"),path=require("path"),puppeteer=require("puppeteer"),{pathToFileURL}=require("url");
async function main(){
 const root=path.resolve(__dirname,".."),plan=await fs.readJson(path.join(root,"temp/drawing_plan.json"));
 const fps=Number(process.env.FPS||30),width=Number(process.env.WIDTH||1920),height=Number(process.env.HEIGHT||1080),duration=Number(plan.duration);
 if(!Number.isFinite(duration)||duration<=0||!plan.words?.length)throw Error("Invalid drawing plan: missing duration or aligned words");
 const count=Math.ceil(duration*fps),maxFrames=Number(process.env.MAX_FRAMES||90000);
 if(count>maxFrames)throw Error(`Render needs ${count} frames; configured safety limit is ${maxFrames}. Lower FPS or shorten the song.`);
 const out=path.join(root,"temp/frames");await fs.emptyDir(out);
 const browser=await puppeteer.launch({headless:true,args:["--no-sandbox","--disable-setuid-sandbox","--disable-dev-shm-usage","--disable-gpu"]});
 let page;
 try{
  page=await browser.newPage();await page.setViewport({width,height,deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(__dirname,"index.html")).href,{waitUntil:"load"});
  await page.waitForFunction(()=>!!window.PencilSketch&&window.__rendererReady===false);
  await page.evaluate(p=>window.PencilSketch.loadPlan(p),plan);
  const batch=Number(process.env.LOG_EVERY_FRAMES||150);
  for(let i=0;i<count;i++){
   await page.evaluate(t=>window.PencilSketch.drawFrame(t),i/fps);
   await page.screenshot({path:path.join(out,"frame_"+String(i+1).padStart(8,"0")+".png"),type:"png"});
   if((i+1)%batch===0)console.log(`[render] ${i+1}/${count} frames (${Math.round((i+1)/count*100)}%)`);
  }
  console.log("[render] Frames saved:",out);
 }finally{if(page)await page.close();await browser.close()}
}
main().catch(e=>{console.error("[render error]",e);process.exit(1)});
