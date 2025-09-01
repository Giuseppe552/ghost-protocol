#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

PROFILE_NAME = "ghostshield"
PROFILE_DIR = Path.home() / ".mozilla" / "firefox" / PROFILE_NAME


def which(env, exe):
    p = os.environ.get(env) or shutil.which(exe)
    if not p:
        raise FileNotFoundError(f"{exe} not found. Install it or set {env}.")
    return p


def ensure_profile(firefox: str) -> Path:
    d = PROFILE_DIR
    if not d.exists() or not (d / "compatibility.ini").exists():
        d.mkdir(parents=True, exist_ok=True)
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
user_pref("network.trr.mode", 5);
"""
    (d / "user.js").write_text(prefs, encoding="utf-8")


def main():
    firefox = which("FIREFOX_PATH", "firefox")
    prof = ensure_profile(firefox)
    write_userjs(prof)

    # NOTE: no --no-remote. Opening URLs later will land in this running window.
    args = [firefox, "-profile", str(prof), "-private-window", "https://check.torproject.org/"]
    subprocess.Popen(args)
    print(json.dumps({"profile_dir": str(prof)}, indent=2))
    print("[i] Launched hardened Firefox. This will accept --new-tab from sidecar.")
    print("[i] Close all Firefox windows first if you had an old --no-remote instance.")


if __name__ == "__main__":
    main()
