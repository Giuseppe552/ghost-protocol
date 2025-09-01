import json, threading, time, socket, subprocess, webbrowser, argparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk

try:
    import requests
except Exception:
    print("pip install -r requirements.txt first (requests[socks])")
    raise

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

TOR_SOCKS = "socks5h://127.0.0.1:9050"
PROX = {"http": TOR_SOCKS, "https": TOR_SOCKS}


def tor_running() -> bool:
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", 9050))
        return True
    except Exception:
        return False
    finally:
        s.close()


def get_exit_ip():
    try:
        r = requests.get("https://check.torproject.org/api/ip", proxies=PROX, timeout=10)
        return r.json()  # {"IsTor": true/false, "IP": "..."}
    except Exception as e:
        return {"error": str(e)}


def dns_compare():
    try:
        local_ip = socket.gethostbyname("example.com")
    except Exception:
        local_ip = "?"
    try:
        r = requests.get("https://dns.google/resolve?name=example.com", proxies=PROX, timeout=10)
        via_tor = r.json().get("Answer", [{}])[0].get("data", "?")
    except Exception:
        via_tor = "?"
    return {"dns_local": local_ip, "dns_via_tor": via_tor}


def https_only_note():
    # Tor Browser enforces HTTPS-Only by default; we provide a button to test it in-browser.
    return {"advice": "Tor Browser uses HTTPS-Only by default. Use the test button to verify."}


class App(tk.Tk):
    def __init__(self, geometry=None):
        super().__init__()
        self.title("Ghost Shield — Sidecar")
        if geometry:
            self.geometry(geometry)
        self.minsize(360, 260)

        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except Exception:
            pass

        self._make_ui()
        self._refresh_async()
        self.after(20000, self._ticker)

    def _make_ui(self):
        pad = {"padx": 10, "pady": 6}
        self.grid_columnconfigure(1, weight=1)

        self.lab_tor = ttk.Label(self, text="Tor process:")
        self.val_tor = ttk.Label(self, text="checking…", foreground="#6b7280")

        self.lab_ip = ttk.Label(self, text="Exit IP / IsTor:")
        self.val_ip = ttk.Label(self, text="—", foreground="#6b7280")

        self.lab_dns = ttk.Label(self, text="DNS mismatch:")
        self.val_dns = ttk.Label(self, text="—", foreground="#6b7280")

        self.lab_https = ttk.Label(self, text="HTTPS-Only:")
        self.val_https = ttk.Label(self, text="Tor Browser enforces it; use test →", foreground="#6b7280")

        row = 0
        for lab, val in [
            (self.lab_tor, self.val_tor),
            (self.lab_ip, self.val_ip),
            (self.lab_dns, self.val_dns),
            (self.lab_https, self.val_https),
        ]:
            lab.grid(row=row, column=0, sticky="w", **pad)
            val.grid(row=row, column=1, sticky="w", **pad)
            row += 1

        # Buttons
        btnf = ttk.Frame(self)
        btnf.grid(row=row, column=0, columnspan=2, sticky="we", padx=10, pady=8)
        for i in range(4):
            btnf.grid_columnconfigure(i, weight=1)

        ttk.Button(btnf, text="Re-check", command=self._refresh_async).grid(row=0, column=0, sticky="we", padx=4)
        ttk.Button(btnf, text="Open Tor Check", command=lambda: webbrowser.open("https://check.torproject.org/")).grid(
            row=0, column=1, sticky="we", padx=4
        )
        ttk.Button(
            btnf, text="HTTP test (HTTPS-Only)", command=lambda: webbrowser.open("http://http.badssl.com/")
        ).grid(row=0, column=2, sticky="we", padx=4)
        ttk.Button(btnf, text="WebRTC test", command=lambda: webbrowser.open("https://browserleaks.com/webrtc")).grid(
            row=0, column=3, sticky="we", padx=4
        )

        ttk.Separator(self).grid(row=row + 1, column=0, columnspan=2, sticky="we", padx=10, pady=4)
        ttk.Label(self, text="Tip: This app never reads your pages. It only runs test requests via Tor.").grid(
            row=row + 2, column=0, columnspan=2, sticky="w", padx=10, pady=4
        )

    def _set(self, label, ok, text):
        if ok is None:
            label.config(text=text, foreground="#6b7280")
        elif ok:
            label.config(text=f"✅ {text}", foreground="#16a34a")
        else:
            label.config(text=f"❌ {text}", foreground="#dc2626")

    def _refresh_async(self):
        threading.Thread(target=self._refresh, daemon=True).start()

    def _refresh(self):
        # Tor process
        running = tor_running()
        self.after(0, lambda: self._set(self.val_tor, running, "running" if running else "not running"))

        # Exit IP
        ip = get_exit_ip()
        if "error" in ip:
            self.after(0, lambda: self._set(self.val_ip, False, ip["error"]))
        else:
            text = f'{ip.get("IP","?")} (IsTor={ip.get("IsTor")})'
            self.after(0, lambda: self._set(self.val_ip, bool(ip.get("IsTor")), text))

        # DNS compare
        dns = dns_compare()
        if "?" in (dns.get("dns_local"), dns.get("dns_via_tor")):
            self.after(0, lambda: self._set(self.val_dns, None, "inconclusive"))
        else:
            same = dns["dns_local"] == dns["dns_via_tor"]
            txt = "same resolver" if same else "different via Tor"
            self.after(0, lambda: self._set(self.val_dns, (not same), txt))

        # HTTPS-only note
        self.after(0, lambda: self._set(self.val_https, None, "Tor Browser enforces it; use test →"))

    def _ticker(self):
        self._refresh_async()
        self.after(20000, self._ticker)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geometry", help="WxH+X+Y (e.g., 480x1080+0+0)")
    args = ap.parse_args()
    App(geometry=args.geometry).mainloop()


if __name__ == "__main__":
    main()
