function callNative(payload){return new Promise((resolve,reject)=>{
  try{
    const port = browser.runtime.connectNative("com.ghostprotocol.host");
    port.onMessage.addListener(msg=>{resolve(msg);port.disconnect();});
    port.onDisconnect.addListener(()=>{if (browser.runtime.lastError) reject(browser.runtime.lastError);});
    port.postMessage(payload);
  }catch(e){reject(e);}
});}

async function httpsOnlyProbe(){
  try{
    const resp = await fetch("http://http.badssl.com/", {method:"GET", cache:"no-store", redirect:"error"});
    return {https_only:false, detail:`HTTP allowed (${resp.status})`};
  }catch(_){ return {https_only:true}; }
}

async function webrtcProbe(timeout=2000){
  return new Promise((resolve)=>{
    let addrs = new Set();
    const pc = new RTCPeerConnection({iceServers:[]});
    pc.createDataChannel("x");
    pc.onicecandidate = e=>{
      if(!e.candidate){
        const ips=[...addrs];
        const leak = ips.some(ip=>/^[0-9]{1,3}(\.[0-9]{1,3}){3}$/.test(ip) && !ip.startsWith("127."));
        resolve({webrtc_leak: leak?true:false, candidates: ips});
      }else{
        const m=e.candidate.candidate.match(/candidate:\S+ \S+ \S+ \S+ (\S+)/);
        if(m&&m[1]) addrs.add(m[1]);
      }
    };
    pc.createOffer().then(o=>pc.setLocalDescription(o));
    setTimeout(()=>{try{pc.close();}catch(_){};
      resolve({webrtc_leak:false, candidates:[...addrs], timeout:true});}, timeout);
  });
}

browser.runtime.onMessage.addListener(async (msg)=>{
  if(msg==="status"){
    const native = await callNative({cmd:"status"}).catch(e=>({error:String(e)}));
    const https = await httpsOnlyProbe();
    const rtc   = await webrtcProbe();
    return {native, https, rtc};
  }else if(msg==="kill_tor"){
    return await callNative({cmd:"kill_tor"}).catch(e=>({error:String(e)}));
  }
});
