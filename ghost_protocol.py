from pathlib import Path
import runpy, sys

root = Path(__file__).resolve().parent
target = root / "tools" / "ghost_protocol.py"
if not target.exists():
    sys.stderr.write("Expected tools/ghost_protocol.py but it was not found.\n")
    sys.exit(1)
runpy.run_path(str(target), run_name="__main__")
