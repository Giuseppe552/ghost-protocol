import subprocess
import time
import webbrowser
import os

# Paths (adjust if needed)
TOR_PATH = r"C:\tor\tor.exe"
FIREFOX_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"

# Firefox Profile (hardened for Tor)
PROFILE_PATH = r"C:\Users\giuse\AppData\Roaming\Mozilla\Firefox\Profiles\tor-secure"

# Ensure profile exists
os.makedirs(PROFILE_PATH, exist_ok=True)

def start_tor():
    print("[+] Starting Tor...")
    return subprocess.Popen([TOR_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def launch_firefox():
    print("[+] Launching Firefox with Tor settings...")

    firefox_args = [
        FIREFOX_PATH,
        "-private-window",
        "-profile", PROFILE_PATH,
        "--no-remote",
        "https://check.torproject.org/"
    ]

    env = os.environ.copy()
    env["MOZ_FORCE_DISABLE_E10S"] = "1"

    return subprocess.Popen(firefox_args, env=env)

def write_userjs():
    """Write hardened settings into user.js inside profile folder"""
    prefs = f"""
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
    with open(os.path.join(PROFILE_PATH, "user.js"), "w") as f:
        f.write(prefs)
    print("[+] Hardened Firefox profile written.")

def main():
    write_userjs()
    tor_proc = start_tor()
    print("[+] Waiting for Tor circuits to bootstrap (15s)...")
    time.sleep(15)

    launch_firefox()
    print("[+] Done. Check browser window for Tor status.")

if __name__ == "__main__":
    main()
