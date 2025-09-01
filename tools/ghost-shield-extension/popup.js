function cls(ok){return ok?"ok":"bad";}
async function refresh(){
  const res = await browser.runtime.sendMessage("status");
  const t=document.getElementById("tor"),
        eip=document.getElementById("exitip"),
        https=document.getElementById("https"),
        rtc=document.getElementById("webrtc"),
        dns=document.getElementById("dns");

  if(res.native?.tor_process?.running){ t.textContent="✅ running"; t.className="ok"; }
  else { t.textContent="❌ not running"; t.className="bad"; }

  const ip = res.native?.report?.ip_check?.IP;
  const isTor = res.native?.report?.ip_check?.IsTor===true;
  eip.textContent = ip ? `${isTor?"✅":"⚠️"} ${ip}` : "—";
  eip.className = ip ? (isTor?"ok":"bad") : "muted";

  https.textContent = res.https?.https_only ? "✅ blocked" : "❌ allowed";
  https.className = cls(res.https?.https_only);

  const leak = res.rtc?.webrtc_leak;
  rtc.textContent = leak ? "❌ local IP exposed" : "✅ no leak";
  rtc.className = cls(!leak);

  const dlocal = res.native?.report?.dns_check?.dns_local;
  const dtor   = res.native?.report?.dns_check?.dns_via_tor;
  if(dlocal && dtor){
    dns.textContent = (dlocal===dtor) ? "⚠️ same resolver" : "✅ different via Tor";
    dns.className = (dlocal===dtor) ? "bad" : "ok";
  }else{ dns.textContent="—"; dns.className="muted"; }
}
document.getElementById("refresh").onclick=refresh;
document.getElementById("kill").onclick=async()=>{ await browser.runtime.sendMessage("kill_tor"); refresh(); };
refresh();
