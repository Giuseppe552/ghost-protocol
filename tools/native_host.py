#!/usr/bin/env python3
import json
import sys
import subprocess
import socket
import pathlib
ROOT   = pathlib.Path(__file__).resolve().parents[1]
TOOLS  = ROOT / "tools"
SCRIPT = TOOLS / "tor_leak_test.py"
REPORT = ROOT / "tor_leak_report.json"




def _read():
    raw = sys.stdin.buffer.read(4)
    if not raw: sys.exit(0)
    n = int.from_bytes(raw, "little")
    data = sys.stdin.buffer.read(n)
    return json.loads(data.decode("utf-8"))




def _send(obj):
    b = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(len(b).to_bytes(4, "little"))
    sys.stdout.buffer.write(b)
sys.stdout.flush()




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




def run_leak_test():
    try:
        subprocess.run([sys.executable, str(SCRIPT)], check=True, timeout=15)
        if REPORT.exists():
            return json.loads(REPORT.read_text())
        return {"error": "no report produced"}
    except Exception as e:
        return {"error": str(e)}




def main():
    while True:
        try:
            req = _read()
        except SystemExit:
            return
        except Exception as e:
            _send({"ok": False, "error": f"read:{e}"})
continue

        if req.get("cmd", "status") == "status":
            _send({
                "ok": True,
                "host": "com.ghostprotocol.host",
                "tor_process": {"running": tor_running()},
                "report": run_leak_test()
            })
        else:
            _send({"ok": False, "error": "unknown cmd"})

if __name__ == "__main__":
    main()
