const {chromium}=require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{
  const [,,fromT,toT,step,outDir]=process.argv; fs.mkdirSync(outDir,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+path.resolve(__dirname,'anim.html')); await p.evaluate(()=>document.fonts.ready);
  let i=0; for(let t=+fromT;t<=+toT+1e-9;t+=+step){await p.evaluate(t=>window.render(t),t);
    await p.screenshot({path:path.join(outDir,String(i).padStart(4,'0')+'.jpg'),type:'jpeg',quality:92}); i++;}
  await b.close(); console.log('frames',i);
})();
