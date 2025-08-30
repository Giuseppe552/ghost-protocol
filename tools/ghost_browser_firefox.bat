@echo off
echo [+] Starting Ghost Browser with Tor...

REM Start Tor in background
start "" "C:\tor\tor.exe" -f "C:\tor\torrc"

REM Wait 15 seconds for Tor to bootstrap
timeout /t 15 >nul

REM Launch Firefox with Tor profile
start "" "C:\Program Files\Mozilla Firefox\firefox.exe" -P ghosttor -no-remote -private-window https://check.torproject.org/

exit
