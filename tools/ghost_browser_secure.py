import atexit, json, os, shutil, subprocess, tempfile, time


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


def make_temp_profile() -> str:
    d = tempfile.mkdtemp(prefix="ghost-tor-profile-")
    atexit.register(lambda: shutil.rmtree(d, ignore_errors=True))
    return d


def write_userjs(profile_dir: str) -> None:
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
    with open(os.path.join(profile_dir, "user.js"), "w") as f:
        f.write(prefs)


def start_tor():
    tor = resolve_tor_path()
    proc = subprocess.Popen([tor], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    atexit.register(lambda: (proc.terminate(), proc.wait(timeout=3)) if proc.poll() is None else None)
    return proc


def launch_firefox(profile_dir: str):
    fx = resolve_firefox_path()
    args = [fx, "-private-window", "-profile", profile_dir, "--no-remote", "https://check.torproject.org/"]
    return subprocess.Popen(args)


def main():
    profile_dir = make_temp_profile()
    write_userjs(profile_dir)
    print("[+] Hardened Firefox profile:", profile_dir)
    tor = start_tor()
    print("[+] Tor PID:", tor.pid, " — waiting 15s to bootstrap...")
    time.sleep(15)
    launch_firefox(profile_dir)
    print(json.dumps({"profile_dir": profile_dir}, indent=2))


if __name__ == "__main__":
    main()
