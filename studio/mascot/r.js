const {chromium}=require('playwright');const {mascot}=require('./m.js');const fs=require('fs');
const FONT='/home/user/-ai_employees-/studio/fonts/NotoSansCJK-Black.ttc';
(async()=>{const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:1});
 const css=`<style>@font-face{font-family:NB;src:url(file://${FONT})}body{margin:0}</style>`;
 // 1) メインの絵
 await p.setViewportSize({width:1024,height:1024});
 await p.setContent(`${css}<div style="width:1024px;height:1024px;background:#cfe6fb;display:flex;align-items:center;justify-content:center">${mascot({w:900,h:930,pose:'point'})}</div>`);
 await p.waitForTimeout(300);await p.screenshot({path:'main.png'});
 // 2) スタンプの見本8個（370x320・背景なし）
 const S=[['wave','smile','おつかれ！'],['point','smile','行こう！'],['yay','happy','やったー！'],['point','wink','まだ枠あるよ'],['wave','happy','ありがとう'],['yay','wow','えっ！'],['wave','sweat','休んで大丈夫'],['point','smile','了解！']];
 fs.mkdirSync('stamps',{recursive:true});
 await p.setViewportSize({width:370,height:320});
 for(const [i,[pose,face,t]] of S.entries()){await p.setContent(`${css}${mascot({pose,face,text:t})}`);await p.waitForTimeout(150);await p.screenshot({path:`stamps/${String(i+1).padStart(2,'0')}.png`,omitBackground:true});}
 // 3) 一覧
 await p.setViewportSize({width:1480,height:640});
 await p.setContent(`${css}<div style="display:grid;grid-template-columns:repeat(4,370px);background:#eef3f8">${S.map(([pose,face,t])=>mascot({pose,face,text:t})).join('')}</div>`);
 await p.waitForTimeout(300);await p.screenshot({path:'sheet.png'});await b.close();})();
