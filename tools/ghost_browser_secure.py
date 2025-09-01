cat > tools/ghost_browser_secure.py << 'EOF'
import os, shutil, subprocess, tempfile, time, sys, json, pathlib

def resolve_tor_path() -> str:
    p = os.environ.get("TOR_PATH")
    if p and os.path.exists(p):
        return p
    p = shutil.which("tor")
    if p:
        return p
    for cand in (
        r"C:\tor\tor.exe",
        r"C:\Program Files\Tor\tor.exe",
        r"C:\Program Files (x86)\Tor\tor.exe",
        r"C:\Users\%USERNAME%\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
    ):
        cand = os.path.expandvars(cand)
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError("Tor not found. Install tor or set TOR_PATH=/full/path/to/tor(.exe)")

def resolve_firefox_path() -> str:
    p = os.environ.get("FIREFOX_PATH")
    if p and os.path.exists(p):
        return p
    p = shutil.which("firefox")
    if p:
        return p
    for cand in (
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ):
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError("Firefox not found in PATH. Install it or set FIREFOX_PATH.")

def write_userjs(profile_dir: str):
    prefs = r'''
user_pref("network.proxy.type", 1);
user_pref("network.proxy.socks", "127.0.0.1");
user_pref("network.proxy.socks_port", 9050);
user_pref("network.proxy.socks_remote_dns", true);
user_pref("network.proxy.no_proxies_on", "");
user_pref("dom.webrtc.enabled", false);
user_pref("privacy.resistFingerprinting", true);
user_pref("browser.contentblocking.category", "strict");
user_pref("dom.security.https_only_mode", true);
'''
    pathlib.Path(profile_dir).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(profile_dir) / "user.js").write_text(prefs, encoding="utf-8")
    print("[+] Hardened Firefox profile written:", profile_dir)

def start_tor():
    tor = resolve_tor_path()
    print("[+] Starting Tor:", tor)
    return subprocess.Popen([tor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def launch_firefox(profile_dir: str):
    firefox = resolve_firefox_path()
    args = [firefox, "-private-window", "-profile", profile_dir, "--no-remote", "https://check.torproject.org/"]
    env = os.environ.copy()
    env["MOZ_FORCE_DISABLE_E10S"] = "1"
    return subprocess.Popen(args, env=env)

def main():
    profile_dir = os.environ.get("PROFILE_DIR") or tempfile.mkdtemp(prefix="ghost-tor-profile-")
    write_userjs(profile_dir)
    tor_proc = start_tor()
    print("[+] Waiting for Tor bootstrap (15s)...")
    time.sleep(15)
    launch_firefox(profile_dir)
    meta = {"profile_dir": profile_dir}
    print(json.dumps(meta, indent=2))
    print("[+] Done. Close Firefox then kill Tor if needed.")

if __name__ == "__main__":
    main()
EOF
