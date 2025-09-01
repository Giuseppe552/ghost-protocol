PY=python3
setup: ; $(PY) -m pip install -r requirements.txt
run:   ; $(PY) ghost_protocol.py
secure:; TOR_PATH=$$(which tor) $(PY) tools/ghost_browser_secure.py
leak:  ; $(PY) tools/tor_leak_test.py && cat tor_leak_report.json
lint:
	$(PY) -m pip install --quiet flake8 black
	flake8 .
	black --check .
