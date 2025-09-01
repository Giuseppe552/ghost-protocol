import json, os, shutil, subprocess, time
from pathlib import Path

PROFILE_NAME = "ghostshield"
PROFILE_DIR = Path.home() / ".mozilla" / "firefox" / PROFILE_NAME

def resolve(cmd_env, fallback):
    p = os.environ.get(cmd_env) or shutil.which(fallback)
    if not p:
        raise FileNotFoundError(f"{fallback} not found. Install it or set {cmd_env}.")
    return p

def confirm(msg):
    try:
        ans = input(f"{msg} [y/N]: ").strip().lower()
    except EOFError:
        ans = ""
    return ans in ("y", "yes")

def ensure_profile(firefox: str) -> Path:
    d = PROFILE_DIR
    if not d.exists() or not (d / "compatibility.ini").exists():
        d.mkdir(parents=True, exist_ok=True)
        # Create a named profile at a fixed path (works with Snap/Flatpak too)
        subprocess.run([firefox, "-CreateProfile", f"{PROFILE_NAME} {str(d)}"], check=True)
        for _ in range(40):
            if (d / "compatibility.ini").exists():
                break
            time.sleep(0.25)
    return d

def write_userjs(d: Path) -> None:
    prefs = """
user_pref("network.proxy.type", 1);
user_pref("network.proxy.socks", "127.0.0.1");
user_pref("network.proxy.socks_port", 9050);
user_pref("network.proxy.socks_remote_dns", true);
user_pref("network.proxy.no_proxies_on", "");
user_pref("dom.webrtc.enabled", false);
user_pref("privacy.resistFingerprinting", true);
user_pref("browser.contentblocking.category", "strict");
user_pref("network.http.referer.XOriginPolicy", 2);
user_pref("dom.security.https_only_mode", true);
"""
    (d / "user.js").write_text(prefs, encoding="utf-8")

def tor_already_running():
    import socket
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", 9050))
        return True
    except Exception:
        return False
    finally:
        s.close()

def main():
    firefox = resolve("FIREFOX_PATH", "firefox")
    tor = resolve("TOR_PATH", "tor")

    # If Firefox is running, offer to open a separate instance (no killing)
    running = subprocess.run(["pgrep", "-x", "firefox"], capture_output=True)
    if running.returncode == 0:
        if not confirm("Firefox is running. Open a separate Tor-hardened window alongside it?"):
            print("Aborted by user.")
            return

    prof = ensure_profile(firefox)
    write_userjs(prof)

    # Start Tor if needed
    if tor_already_running():
        print("[+] Tor already running on 9050 — reusing it.")
    else:
        print("[+] Starting Tor…")
        subprocess.Popen([tor])  # no pkill, no shutdown hooks

    print("[+] Launching Firefox (separate instance, hardened profile)…")
    args = [
        firefox,
        "--new-instance",
        "--no-remote",
        "-profile", str(prof),
        "-private-window",
        "https://check.torproject.org/"
    ]
    subprocess.Popen(args)

    print(json.dumps({"profile_dir": str(prof)}, indent=2))
    print("[i] HTTPS-Only + anti-WebRTC written to user.js.")
    print("[i] No existing Firefox windows were closed.")
    print("[i] To stop Tor later, close it from its own window or `pkill tor` (manually).")

if __name__ == "__main__":
    main()
