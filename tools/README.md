
## 🛡️ Tools

### 1. VPN Leak Test (`vpn_leak_test.py`)

This script performs an **advanced VPN privacy audit** and generates a structured JSON report.  
It is designed to show **where VPNs leak identifying information** — useful for privacy researchers, penetration testers, and security-conscious users.

🔍 It tests for:

- 🌐 **DNS Leaks** – Detects if your system is leaking real DNS servers.
- 🎥 **WebRTC Leaks** – Checks if your local IP is exposed via STUN (common in browsers).
- 🔢 **IPv6 Leaks** – Confirms whether IPv6 traffic escapes the VPN tunnel.
- 📍 **Geolocation Leaks** – Compares VPN IP-based location with system location.

---

#### ⚙️ Usage

```bash
cd tools
python vpn_leak_test.py
````

This creates a report:

```
vpn_leak_report.json
```

---

#### 📝 Example Output

```json
{
  "dns_leak": false,
  "webrtc_leak": true,
  "ipv6_leak": false,
  "geolocation": {
    "ip": "185.199.108.153",
    "country": "Germany",
    "city": "Frankfurt"
  }
}
```

---

#### 🎯 Why This Matters

Most VPN services advertise "no leaks," but real-world setups often fail.
This tool demonstrates:

* How **DNS misconfigurations** expose browsing history.
* Why **WebRTC** is a silent leak vector in most browsers.
* How **IPv6** bypasses legacy VPN tunnels.
* Why **location mismatches** show when your VPN isn’t fully private.

By showing JSON output, this tool can also be integrated into dashboards, reports, or automated red-team pipelines.

---

💡 **Educational Purpose Only**
This tool is part of the Ghost Protocol project, which demonstrates **how anonymity leaks occur** — so that better privacy systems can be designed.

```
