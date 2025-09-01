#!/usr/bin/env python3
import json
import os
import pathlib
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOR_LEAK = TOOLS / "tor_leak_test.py"
PIDFILE = TOOLS / ".tor.pid"


def _read_msg():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        sys.exit(0)
    msg_len = int.from_bytes(raw_len, "little")
    data = sys.stdin.buffer.read(msg_len)
    return json.loads(data.decode("utf-8"))


def _send_msg(obj):
    enc = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(len(enc).to_bytes(4, "little"))
    sys.stdout.buffer.write(enc)
    sys.stdout.flush()


def _tor_running():
    try:
        pid = int(pathlib.Path(PIDFILE).read_text().strip())
        os.kill(pid, 0)
        return True, pid
    except Exception:
        return False, None


def _status():
    try:
        subprocess.run([sys.executable, str(TOR_LEAK)], capture_output=True, text=True, timeout=20)
        report_path = ROOT / "tor_leak_report.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
    except Exception as e:
        report = {"error": f"tor_leak_test failed: {e}"}
    ok, pid = _tor_running()
    return {"tor_process": {"running": ok, "pid": pid}, "report": report, "host": "native-python"}


def main():
    while True:
        try:
            req = _read_msg()
        except SystemExit:
            break
        cmd = req.get("cmd")
        if cmd == "status":
            _send_msg(_status())
        elif cmd == "kill_tor":
            ok, pid = _tor_running()
            if ok:
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.4)
                except Exception as e:
                    _send_msg({"ok": False, "error": str(e)})
                    continue
            _send_msg({"ok": True})
        else:
            _send_msg({"error": f"unknown cmd: {cmd}"})


if __name__ == "__main__":
    main()
