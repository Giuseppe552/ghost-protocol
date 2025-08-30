@echo off
echo [+] Starting Ghost Browser (Chrome Mode)...

REM Start Tor in background
start "" "C:\tor\tor.exe"

REM Wait 15s for Tor to bootstrap
timeout /t 15 >nul

REM Run Tor leak test before launching Chrome
python tools\tor_leak_test.py
echo [+] Pre-launch leak test saved to tor_leak_report.json

REM Launch Chrome forced through Tor
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --proxy-server="socks5://127.0.0.1:9050" ^
  --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE localhost" ^
  --disable-webrtc ^
  --incognito ^
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"

REM Run Tor leak test again after Chrome starts
python tools\tor_leak_test.py
echo [+] Post-launch leak test saved to tor_leak_report.json
pause
