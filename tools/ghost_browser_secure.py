import atexit
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def resolve_tor_path() -> str:
    p = os.environ.get("TOR_PATH") or shutil.which("tor")
    if p:
        return p
    raise FileNotFoundError("Tor not found. Install tor or set TOR_PATH")


def resolve_firefox_path() -> str:
    p = os.environ.get("FIREFOX_PATH") or shutil.which("firefox")
    if p:
        return p
    raise FileNotFoundError("Firefox not found. Install it or set FIREFOX_PATH")


def make_temp_profile() -> Path:
    d = Path(tempfile.mkdtemp(prefix="ghost-tor-profile-"))
    atexit.register(lambda: shutil.rmtree(d, ignore_errors=True))
    return d


def create_profile_dir(firefox: str, profile_dir: Path) -> None:
    # Initialize the profile folder so Firefox won’t show “Profile Missing”
    subprocess.run([firefox, "-CreateProfile", f"ghostshield {profile_dir}"], check=True)


def write_userjs(profile_dir: Path) -> None:
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
    (profile_dir / "user.js").write_text(prefs, encoding="utf-8")


def start_tor(pidfile: Path):
    tor = resolve_tor_path()
    proc = subprocess.Popen([tor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pidfile.write_text(str(proc.pid))

    def _kill():
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    atexit.register(_kill)
    return proc


def launch_firefox(profile_dir: Path):
    fx = resolve_firefox_path()
    args = [
        fx,
        "-private-window",
        "-profile",
        str(profile_dir),
        "--no-remote",
        "https://check.torproject.org/",
    ]
    return subprocess.Popen(args)


def main():
    fx = resolve_firefox_path()
    profile_dir = make_temp_profile()
    create_profile_dir(fx, profile_dir)
    write_userjs(profile_dir)
    pidfile = Path(__file__).parent / ".tor.pid"
    print("[+] Hardened Firefox profile:", profile_dir)
    tor = start_tor(pidfile)
    print("[+] Tor PID:", tor.pid, "— waiting 15s to bootstrap...")
    time.sleep(15)
    launch_firefox(profile_dir)
    print(json.dumps({"profile_dir": str(profile_dir)}, indent=2))


if __name__ == "__main__":
    main()
