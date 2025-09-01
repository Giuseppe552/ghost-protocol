#!/usr/bin/env python3
import json, socket, subprocess, sys, os, shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk

ROOT   = Path(__file__).resolve().parents[1]
TOOLS  = ROOT / "tools"
TOR_LEAK = TOOLS / "tor_leak_test.py"
REPORT  = ROOT / "tor_leak_report.json"

# ---------- helpers ----------
def tor_running(host="127.0.0.1", port=9050, timeout=0.4) -> bool:
    s = socket.socket(); s.settimeout(timeout)
    try:
        s.connect((host, port)); return True
    except Exception:
        return False
    finally:
        s.close()

def run_leak_test():
    try:
        subprocess.run([sys.executable, str(TOR_LEAK)], check=True, timeout=20, cwd=str(ROOT))
        if REPORT.exists():
            return json.loads(REPORT.read_text())
    except Exception:
        pass
    return {}

def open_in_tor(url: str):
    firefox = os.environ.get("FIREFOX_PATH") or shutil.which("firefox")
    prof = Path.home() / ".mozilla" / "firefox" / "ghostshield"
    subprocess.Popen([
        firefox, "--new-instance", "--no-remote",
        "-profile", str(prof), "-private-window", url
    ])

GREEN = "#16a34a"; RED = "#dc2626"; MUTE = "#6b7280"

# ---------- UI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ghost Shield — Sidecar")
        self._init_scaling()
        self._init_geometry()
        self._build_ui()
        self.after(100, self.refresh)
        self.after(2500, self._tick)  # live updates

    def _init_scaling(self):
        # Make text comfortable on HiDPI/LoDPI
        try:
            px = self.winfo_fpixels('1i')  # pixels per inch
            scaling = 1.4 if px >= 160 else 1.0
            self.tk.call('tk', 'scaling', scaling)
        except Exception:
            pass

    def _init_geometry(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w = max(420, int(sw * 0.25))
        h = min(760, int(sh * 0.92))
        self.geometry(f"{w}x{h}+10+40")
        self.minsize(420, 420)
        self.resizable(True, True)

    def _build_ui(self):
        big   = ("Sans", 16)
        small = ("Sans", 12)

        self.style = ttk.Style(self)
        self.style.configure("TLabel", font=big)
        self.style.configure("Small.TLabel", font=small, foreground=MUTE)
        self.style.configure("TButton", font=big)

        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        # Status area (scrollable if small screens)
        canvas = tk.Canvas(root, highlightthickness=0)
        vsb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        self.status_frame = ttk.Frame(canvas)
        self.status_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.status_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.l_tor   = ttk.Label(self.status_frame, text="Tor process: …")
        self.l_ip    = ttk.Label(self.status_frame, text="Exit IP / IsTor: …")
        self.l_dns   = ttk.Label(self.status_frame, text="DNS mismatch: …")
        self.l_https = ttk.Label(self.status_frame, text="HTTPS-Only: Tor Browser enforces it; use tests →")
        for w in (self.l_tor, self.l_ip, self.l_dns, self.l_https):
            w.pack(anchor="w", pady=(0,6))

        ttk.Label(self.status_frame,
                  text="Live view only runs test requests; it never reads your tabs.",
                  style="Small.TLabel").pack(anchor="w", pady=(2,10))

        # Buttons (one per line)
        self.live = tk.BooleanVar(value=True)
        box = ttk.Frame(self.status_frame); box.pack(fill="x")
        ttk.Button(box, text="Re-check now", command=self.refresh).pack(fill="x", pady=6)
        ttk.Button(box, text="Open Tor Check", command=lambda: open_in_tor("https://check.torproject.org/")).pack(fill="x", pady=6)
        ttk.Button(box, text="HTTP test (should block)", command=lambda: open_in_tor("http://http.badssl.com/")).pack(fill="x", pady=6)
        ttk.Button(box, text="WebRTC test page", command=lambda: open_in_tor("https://browserleaks.com/webrtc")).pack(fill="x", pady=6)
        ttk.Checkbutton(box, text="Live refresh every 2.5s", variable=self.live).pack(anchor="w", pady=(8,0))

    def _set(self, label: ttk.Label, ok: bool | None, text: str):
        if ok is None:
            label.configure(text=text, foreground=MUTE)
        else:
            label.configure(text=("✓ " if ok else "✗ ") + text,
                            foreground=(GREEN if ok else RED))

    def refresh(self):
        running = tor_running()
        self._set(self.l_tor, running, "Tor process: " + ("running" if running else "not running"))

        rep = run_leak_test() if running else {}
        ip = rep.get("ip_check", {}).get("IP")
        is_tor = rep.get("ip_check", {}).get("IsTor")
        if ip:
            self._set(self.l_ip, bool(is_tor), f"Exit IP / IsTor: {ip} (IsTor={is_tor})")
        else:
            self._set(self.l_ip, None, "Exit IP / IsTor: —")

        dlocal = rep.get("dns_check", {}).get("dns_local")
        dtor   = rep.get("dns_check", {}).get("dns_via_tor")
        if dlocal and dtor:
            self._set(self.l_dns, dlocal != dtor,
                      ("DNS mismatch: different via Tor" if dlocal != dtor else "DNS mismatch: same resolver"))
        else:
            self._set(self.l_dns, None, "DNS mismatch: —")

        self._set(self.l_https, None, "HTTPS-Only: Tor Browser enforces it; use tests →")

    def _tick(self):
        if self.live.get():
            self.refresh()
        self.after(2500, self._tick)

if __name__ == "__main__":
    App().mainloop()
