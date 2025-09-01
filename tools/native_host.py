#!/usr/bin/env python3
import json
import pathlib
import socket
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
REPORT = ROOT / "tor_leak_report.json"
SCRIPT = TOOLS / "tor_leak_test.py"


def _read():
    raw = sys.stdin.buffer.read(4)
    if not raw:
        sys.exit(0)
    n = int.from_bytes(raw, "little")
    data = sys.stdin.buffer.read(n)
    return json.loads(data.decode("utf-8"))


def _send(obj):
    b = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(len(b).to_bytes(4, "little"))
    sys.stdout.buffer.write(b)
    sys.stdout.buffer.flush()


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


def run_leak_test(timeout: int = 15):
    try:
        subprocess.run([sys.executable, str(SCRIPT)], check=True, timeout=timeout)
    except Exception:
        pass
    if REPORT.exists():
        try:
            return json.loads(REPORT.read_text())
        except Exception:
            return None
    return None


def main():
    while True:
        try:
            req = _read()
        except SystemExit:
            return
        except Exception as e:
            _send({"error": f"read_error: {e}"})
            continue

        cmd = req.get("cmd", "status")
        if cmd == "status":
            _send({"tor_process": {"running": tor_running()}, "report": run_leak_test()})
        else:
            _send({"error": "unknown_cmd", "cmd": cmd})


if __name__ == "__main__":
    main()
