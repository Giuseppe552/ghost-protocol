#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess


def open_tor_check():
    firefox = shutil.which("firefox")
    if not firefox:
        return False
    prof = Path.home() / ".mozilla" / "firefox" / "ghostshield"
    args = [
        firefox,
        "--new-instance",
        "--no-remote",
        "-profile",
        str(prof),
        "-private-window",
        "https://check.torproject.org/",
    ]
    subprocess.Popen(args)
    return True


def main():
    open_tor_check()


if __name__ == "__main__":
    main()
