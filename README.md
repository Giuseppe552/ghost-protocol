# 🕵️ Ghost Protocol

*A research + demo lab for digital anonymity (Linux-first, 2025).*

> “If you can’t explain it to a 5-year-old, you don’t understand it well enough.”

Ghost Protocol shows — with **plain-English notes** and **working Python tools** — how identity leaks happen on the web, and how to test/mitigate them:
- HTTPS-only browsing and Tor routing
- WebRTC/DNS/IP leak checks
- Metadata stripping for JPG/PDF/DOCX

> **Ethics & intent:** This project is for **education and research** so builders can design **safer systems**. Don’t use it to break the law or harm people.

---

## 📦 What’s inside

```

ghost-protocol/
├─ docs/                  # Short explainers + deep dives
├─ tools/
│  ├─ ghost\_protocol.py   # Interactive AIO tool (menu)
│  ├─ ghost\_browser\_secure.py  # Hardened Firefox + Tor (HTTPS-only, WebRTC off)
│  ├─ tor\_leak\_test.py    # IP/DNS leak check via Tor
│  ├─ metadata\_cleaner.py # Strip metadata from JPG/PDF/DOCX
│  └─ vpn\_leak\_test.py    # Basic DNS/IPv6/WebRTC checks (optional)
├─ ghost\_protocol.py      # Root launcher -> tools/ghost\_protocol.py
├─ requirements.txt
├─ Makefile               # Quality-of-life targets (optional)
└─ .github/workflows/     # CI (lint + import check)

````

---

## ⚙️ Requirements (Linux)

- Python **3.10+**
- Tor (`sudo apt install -y tor`)
- Firefox (preinstalled on most distros)

> The Python dependencies are installed from `requirements.txt`.  
> `geckodriver` is **not** required for the current tooling.

---


## 🧪 Usage

### 1) Interactive AIO tool

```bash
python3 ghost_protocol.py
```

You’ll get a small menu to:

* make HTTPS requests via Tor,
* clean file metadata (JPG/PDF/DOCX).

### 2) Hardened browser via Tor (HTTPS-only, WebRTC disabled)

```bash
python3 tools/ghost_browser_secure.py
```

What to expect:

* Firefox opens on `check.torproject.org` with a new hardened profile
* **HTTP** sites show “HTTPS-Only Mode” blocked page (by design)
* WebRTC leak tests show **No Leak**

### 3) Tor leak check (headless)

```bash
python3 tools/tor_leak_test.py
cat tor_leak_report.json
```

Example output:

```json
{
  "ip_check": {"IsTor": true, "IP": "45.84.107.33"},
  "dns_check": {"dns_local": "23.192.228.80", "dns_via_tor": "23.215.0.138"}
}
```

### 4) Metadata cleaner

```bash
# JPG/PNG
python3 tools/metadata_cleaner.py --in samples/cleaned_demo.jpg --out out.jpg

# PDF
python3 tools/metadata_cleaner.py --in samples/cleaned_demo.pdf --out out.pdf

# DOCX
python3 tools/metadata_cleaner.py --in samples/cleaned_demo.docx --out out.docx
```

---

## 🧠 What you’ll learn (short versions)

* **Encryption vs. anonymity:** encryption hides *content*, anonymity hides *who*. You need both.
* **Signal is private, not anonymous:** E2EE but phone-number metadata ties identity.
* **Metadata wins:** timing/IP/graph info often deanonymizes even if messages are encrypted.

---

## 🧹 Dev quality

* CI: flake8 + import/compile check (Linux)
* Code style: Black + flake8 (configured)
* `.gitignore` blocks build artifacts and local reports

Run locally:

```bash
make fmt      # black .
make lint     # flake8 + py_compile
```

---

## 🗺️ Roadmap

* [x] Linux-first Tor browser hardening
* [x] WebRTC/DNS leak tests
* [x] Metadata cleaner (JPG/PDF/DOCX)
* [ ] CLI subcommands (non-interactive `browser | leak | clean`)
* [ ] **Ghost Dashboard**: one-page summary of leaks & mitigations
* [ ] Packaging for `pipx` + .deb install script

---

## 📝 License

MIT — see `LICENSE`.

---

## 🤝 Contributing

Issues and PRs welcome. Keep PRs small and Linux-first. Run `make fmt && make lint` before pushing.





### ▶️ One-liner demo (Linux, Firefox)

```
bash -c 'set -e; cd ~; REPO=ghost-protocol; [ -d "$REPO" ] || git clone https://github.com/Giuseppe552/ghost-protocol.git "$REPO"; cd "$REPO"; git pull --rebase || true; python3 -m pip install --user -r requirements.txt >/dev/null 2>&1 || true; python3 -c "import tkinter" 2>/dev/null || (sudo apt-get update -y && sudo apt-get install -y python3-tk); mkdir -p ~/.mozilla/firefox/ghostshield; printf "\nuser_pref(\"network.trr.mode\", 5);\n" >> ~/.mozilla/firefox/ghostshield/user.js; GP_ASSUME_YES=1 python3 tools/ghost_browser_secure.py >/dev/null 2>&1 & sleep 3; python3 tools/ghost_sidecar.py'

```

