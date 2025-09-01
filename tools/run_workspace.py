import os
import shutil
import subprocess
import time
from pathlib import Path
import tkinter as tk

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "tools" / "ghost_dashboard.py"
BROWSER_LAUNCH = ROOT / "tools" / "ghost_browser_secure.py"




def screen_size():
    # use Tk to read screen dimensions
    r = tk.Tk()
r.withdraw()
    w, h = r.winfo_screenwidth(), r.winfo_screenheight()
    r.destroy()
    return w, h




def try_tile_firefox(x, y, w, h):
    # works on X11 if wmctrl present
no-op on Wayland
    if shutil.which("wmctrl") and os.environ.get("XDG_SESSION_TYPE", "x11") == "x11":
        # wait for window to appear
        for _ in range(50):
            out = subprocess.check_output(["wmctrl", "-lG"]).decode("utf-8", "ignore")
            cand = [line.split() for line in out.splitlines() if "Firefox" in line]
            if cand:
                wid = cand[-1][0]
                geom = f"0, {x}, {y}, {w}, {h}"
                subprocess.call(["wmctrl", "-i", "-r", wid, "-e", geom])
                break
            time.sleep(0.3)




def main():
    sw, sh = screen_size()
    left_w = int(sw * 0.25)
    right_w = sw - left_w

    # 1) Launch dashboard on the left
    dash_geom = f"{left_w}x{sh}+0+0"
    subprocess.Popen(["python3", str(DASH), "--geometry", dash_geom])

    # 2) Launch hardened Firefox on the right (through Tor)
    subprocess.Popen(["python3", str(BROWSER_LAUNCH)])

    # 3) Try to tile Firefox to the right 3/4 (best-effort)
    try_tile_firefox(left_w, 0, right_w, sh)

if __name__ == "__main__":
    main()
