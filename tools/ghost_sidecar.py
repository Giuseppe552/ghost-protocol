#!/usr/bin/env python3
import json
import socket
import subprocess
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SCRIPT = TOOLS / "tor_leak_test.py"
REPORT = ROOT / "tor_leak_report.json"

BIG = ("DejaVu Sans", 26)
MED = ("DejaVu Sans", 20)
SM = ("DejaVu Sans", 14)

TOR_CHECK = "https://check.torproject.org/"
HTTP_TEST = "http://http.badssl.com/"
WEBRTC_TEST = "https://browserleaks.com/webrtc"


def tor_running() -> bool:
    s = socket.socket()
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", 9050))
        return True
    except Exception:
        return False
    finally:
        s.close()


def run_leak_test():
    try:
        subprocess.run([sys.executable, str(SCRIPT)], check=True, timeout=12)
        return json.loads(REPORT.read_text()) if REPORT.exists() else {}
    except Exception as e:
        return {"error": str(e)}


def summarize(ok_tor, is_tor, dns_diff):
    if ok_tor and is_tor and dns_diff:
        return ("You’re protected (Tor OK, exit is Tor, DNS differs).", "#16a34a")
    if not ok_tor:
        return ("Tor SOCKS not reachable on 9050.", "#dc2626")
    if not is_tor:
        return ("Exit IP is not a Tor node.", "#dc2626")
    if not dns_diff:
        return ("DNS resolver the same inside/outside Tor.", "#f97316")
    return ("Mixed status — recheck.", "#f59e0b")


class App:
    def __init__(self):
        self.w = tk.Tk()
        self.w.title("Ghost Shield — Sidecar")
        self.w.geometry("820x560+20+40")
        self.w.configure(bg="#e5e7eb")

        self.l1 = tk.Label(self.w, text="✓ Tor process: …", font=BIG, fg="#10b981", bg="#e5e7eb")
        self.l2 = tk.Label(self.w, text="✓ Exit IP / IsTor: …", font=BIG, fg="#10b981", bg="#e5e7eb")
        self.l3 = tk.Label(self.w, text="✓ DNS mismatch: …", font=BIG, fg="#10b981", bg="#e5e7eb")
        self.l4 = tk.Label(
            self.w,
            text="HTTPS-Only: Tor Browser enforces it; use tests →",
            font=MED,
            fg="#6b7280",
            bg="#e5e7eb",
        )
        self.sum = tk.Label(self.w, text="Summary…", font=MED, fg="#374151", bg="#e5e7eb")

        for i, l in enumerate((self.l1, self.l2, self.l3, self.l4, self.sum)):
            l.pack(anchor="w", padx=18, pady=(10 if i == 0 else 4, 0))

        btns = (
            ("Re-check now", self.refresh),
            ("Copy Tor Check URL", lambda: self.copy_url(TOR_CHECK)),
            ("Copy HTTP test URL", lambda: self.copy_url(HTTP_TEST)),
            ("Copy WebRTC test URL", lambda: self.copy_url(WEBRTC_TEST)),
        )
        for text, cmd in btns:
            b = tk.Button(self.w, text=text, font=MED, height=1, command=cmd)
            b.pack(fill="x", padx=18, pady=8)

        self.hint = tk.Label(
            self.w,
            text="Tip: click a button → it’s copied. In Tor press Ctrl+L, Ctrl+V, Enter.",
            font=SM,
            fg="#374151",
            bg="#e5e7eb",
        )
        self.hint.pack(anchor="w", padx=12, pady=(8, 0))

        self.tick = tk.Label(self.w, text="• Live refresh every 10s", font=SM, fg="#374151", bg="#e5e7eb")
        self.tick.pack(anchor="w", padx=12, pady=(4, 0))

        self.refresh()
        self.w.after(10000, self.auto)  # 10 seconds
        self.w.mainloop()

    def copy_url(self, url: str):
        self.w.clipboard_clear()
        self.w.clipboard_append(url)
        self.hint.config(text=f"Copied: {url}  →  In Tor: Ctrl+L, Ctrl+V, Enter.")

    def auto(self):
        self.refresh()
        self.w.after(10000, self.auto)

    def refresh(self):
        data = run_leak_test()
        ok_tor = tor_running()
        ip = data.get("ip_check", {}).get("IP")
        is_tor = data.get("ip_check", {}).get("IsTor") is True
        dns_local = data.get("dns_check", {}).get("dns_local")
        dns_tor = data.get("dns_check", {}).get("dns_via_tor")
        dns_diff = bool(dns_local and dns_tor and dns_local != dns_tor)

        self.l1.config(
            text=f"{'✓' if ok_tor else '✗'} Tor process: {'running' if ok_tor else 'not reachable'}",
            fg=("#10b981" if ok_tor else "#dc2626"),
        )
        self.l2.config(
            text=f"{'✓' if is_tor else '✗'} Exit IP / IsTor: {ip or '—'} (IsTor={bool(is_tor)})",
            fg=("#10b981" if is_tor else "#dc2626"),
        )
        self.l3.config(
            text=f"{'✓' if dns_diff else '✗'} DNS mismatch: " f"{'different via Tor' if dns_diff else 'same resolver'}",
            fg=("#10b981" if dns_diff else "#dc2626"),
        )

        msg, color = summarize(ok_tor, is_tor, dns_diff)
        self.sum.config(text=msg, fg=color)


if __name__ == "__main__":
    App()
