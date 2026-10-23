// VM DOM model tests: not Chromium/YouTube or a real media renderer.
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const template=fs.readFileSync('tools/youtube_pip/candidate.js','utf8');
let checks=0;
function model(host='www.youtube.com',top=true,known=true,observed=true){
 class Document {get hidden(){return this.actualHidden;}get visibilityState(){return this.actualHidden?'hidden':'visible';}}
 let pending=[];
 class HTMLVideoElement {
  constructor(){this.attrs=new Map([['disablepictureinpicture','original']]);this.paused=false;this.plays=0;this.isConnected=true;}
  get disablePictureInPicture(){return this.hasAttribute('disablepictureinpicture');}
  set disablePictureInPicture(value){if(value)this.setAttribute('disablepictureinpicture','');else this.removeAttribute('disablepictureinpicture');}
  hasAttribute(name){return this.attrs.has(name);}getAttribute(name){return this.attrs.get(name)??null;}
  setAttribute(name,value){this.attrs.set(name,value);pending.push({type:'attributes',target:this,attributeName:name});}
  removeAttribute(name){if(this.attrs.delete(name))pending.push({type:'attributes',target:this,attributeName:name});}
  pause(){this.paused=true;}play(){this.plays++;throw new Error('Must never play');}
 }
 const doc=new Document();doc.actualHidden=true;
 if(!known)Object.defineProperty(doc,'hidden',{value:true});
 const listeners={},video=new HTMLVideoElement();
 doc.querySelectorAll=()=>[video];doc.querySelector=()=>video;
 doc.addEventListener=(name,fn)=>{listeners[name]=fn;};
 let mutation;
 class MutationObserver {constructor(fn){mutation=fn;}observe(){}takeRecords(){const records=pending;pending=[];return records;}}
 const win={};win.top=top?win:{};
 const context={window:win,document:doc,Document,HTMLVideoElement,MutationObserver:observed?MutationObserver:undefined,navigator:{userActivation:{isActive:false}},location:{hostname:host,protocol:'https:'}};
 const run=options=>vm.runInNewContext(template.replace('__VERSANIUM_OPTIONS__',JSON.stringify(options)),context);
 return {run,doc,video,listeners,mutation:()=>{const records=pending;pending=[];mutation?.(records);}};
}
let m=model();let result=m.run({mobile:true,pip:true,background:true});
assert.equal(result.pipAdjusted,true);checks++;
assert.equal(m.doc.hidden,false);assert.equal(m.doc.visibilityState,'visible');checks+=2;
m.video.paused=true;m.listeners.pause({target:m.video});
assert.equal(m.run({mobile:true,pip:true,background:true}).pauseObserved,true);checks++;
assert.equal(m.video.plays,0);assert.equal(m.video.paused,true);checks+=2;
assert.equal(m.doc.hidden,true);checks++; // A paused video never gets a fake-visible document.
m.video.paused=false;
let stopped=false;m.listeners.visibilitychange({stopImmediatePropagation(){stopped=true;}});assert(stopped);checks++;
m.run({mobile:false,pip:true,background:true});assert.equal(m.doc.hidden,true);checks++;
stopped=false;m.listeners.visibilitychange({stopImmediatePropagation(){stopped=true;}});assert(!stopped);checks++;
m=model();m.run({mobile:true,pip:true,background:false});assert.equal(m.doc.hidden,true);checks++;
m=model();m.run({mobile:true,pip:false,background:true});assert.equal(m.video.disablePictureInPicture,true);checks++;
for(const host of ['twitch.tv','youtube.com.attacker.test','youtu.be']){
 m=model(host);assert.equal(m.run({mobile:true,pip:true,background:true}),null);assert.equal(m.video.disablePictureInPicture,true);checks+=2;
}
m=model('www.youtube.com',false);assert.equal(m.run({mobile:true,pip:true,background:true}),null);checks++;
m=model('www.youtube.com',true,false);m.run({mobile:true,pip:false,background:true});assert.equal(m.doc.hidden,true);checks++;
m=model();m.run({mobile:true,pip:false,background:false,diagnostics:true});m.video.pause();
assert.equal(m.run({mobile:true,pip:false,background:false,diagnostics:true}).pauseMethodObserved,true);checks++;
assert.equal(m.video.paused,true);assert.equal(m.video.plays,0);checks+=2;
m=model();m.video.paused=true;m.run({mobile:true,pip:true,background:true});
assert.equal(m.video.disablePictureInPicture,true);checks++;
m.video.paused=false;m.listeners.play();assert.equal(m.video.disablePictureInPicture,false);checks++;
// Same document round trip: restore precisely the value we owned, then adjust again.
m=model();m.run({mobile:true,pip:true});assert.equal(m.video.disablePictureInPicture,false);checks++;
m.run({mobile:false,pip:true});assert.equal(m.video.disablePictureInPicture,true);checks++;
assert.equal(m.video.getAttribute('disablepictureinpicture'),'original');checks++;
m.run({mobile:true,pip:true});assert.equal(m.video.disablePictureInPicture,false);checks++;
// A site write after our change, even true->false before observer delivery, wins.
m.video.setAttribute('disablepictureinpicture','site-new');m.video.removeAttribute('disablepictureinpicture');
m.run({mobile:false,pip:true});assert.equal(m.video.disablePictureInPicture,false);checks++;
m=model();m.run({mobile:true,pip:true});m.video.setAttribute('disablepictureinpicture','site-new');
m.run({mobile:false,pip:true});assert.equal(m.video.getAttribute('disablepictureinpicture'),'site-new');checks++;
m=model();m.run({mobile:true,pip:true});m.run({mobile:true,pip:false});
assert.equal(m.video.getAttribute('disablepictureinpicture'),'original');checks++;
m=model();m.run({mobile:true,pip:true});m.video.isConnected=false;m.run({mobile:false,pip:true});
assert.equal(m.video.disablePictureInPicture,true);checks++;
m=model();Object.defineProperty(m.video,'disablePictureInPicture',{value:true,writable:true});
m.run({mobile:true,pip:true});assert.equal(m.video.disablePictureInPicture,true);checks++;
m=model('www.youtube.com',true,true,false);m.run({mobile:true,pip:true});
assert.equal(m.video.disablePictureInPicture,true);checks++;
m=model();m.run({mobile:true,pip:true});m.video.isConnected=false;m.mutation();
assert.equal(m.video.getAttribute('disablepictureinpicture'),'original');checks++;
m.video.isConnected=true;m.run({mobile:false,pip:true});assert.equal(m.video.disablePictureInPicture,true);checks++;
console.log(`YouTube candidate: ${checks} DOM-model checks PASS; real playback/PiP unverified`);
