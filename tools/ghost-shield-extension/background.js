async function callNative(payload) {
  const port = browser.runtime.connectNative("com.ghostprotocol.host");
  return await new Promise((resolve, reject) => {
    let done = false;
    port.onMessage.addListener((msg) => { done = true; resolve(msg); port.disconnect(); });
    port.onDisconnect.addListener(() => { if (!done) reject(browser.runtime.lastError); });
    port.postMessage(payload || { cmd: "status" });
  });
}

async function httpsOnlyProbe() {
  try {
    await fetch("http://http.badssl.com/", { redirect: "error", cache: "no-store" });
    return { https_only: false };
  } catch (_) {
    return { https_only: true };
  }
}

async function webrtcProbe() {
  return new Promise((resolve) => {
    const pc = new RTCPeerConnection({ iceServers: [] });
    const addrs = new Set();
    pc.createDataChannel("x");
    pc.onicecandidate = (e) => {
      if (!e.candidate) {
        const ips = [...addrs];
        const leak = ips.some(ip => /^[0-9.]+$/.test(ip) && !ip.startsWith("127."));
        resolve({ webrtc_leak: leak, candidates: ips });
        try { pc.close(); } catch {}
      } else {
        const m = / candidate:\S+ \d+ \S+ \S+ (\S+)/.exec(e.candidate.candidate);
        if (m && m[1]) addrs.add(m[1]);
      }
    };
    pc.createOffer().then(o => pc.setLocalDescription(o));
    setTimeout(() => { try { pc.close(); } catch {}; resolve({ webrtc_leak: false, candidates: [...addrs] }); }, 3000);
  });
}

browser.runtime.onMessage.addListener(async (msg) => {
  if (msg === "status") {
    const [native, https, rtc] = await Promise.all([
      callNative({ cmd: "status" }).catch(e => ({ error: String(e) })),
      httpsOnlyProbe(),
      webrtcProbe()
    ]);
    return { native, https, rtc };
  }
  return { error: "unknown message" };
});
