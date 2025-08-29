## 🛠 Tools

### 1. VPN Leak Test (`vpn_leak_test.py`)

This script performs an **advanced VPN privacy check** and outputs results as JSON for easy integration into dashboards or reports.  
It detects the most common VPN privacy leaks:

- 🌍 **DNS Leaks** — Checks if your system is leaking real DNS servers.
- 🔗 **WebRTC Leaks** — Detects if your local IP is exposed via STUN requests (common in browsers).
- 🌐 **IPv6 Leaks** — Confirms whether IPv6 bypasses the VPN tunnel.
- 📍 **Geolocation Leaks** — Compares VPN IP location vs system location.

#### ✅ Usage

```bash
cd tools
python vpn_leak_test.py

This will create a report:

vpn_leak_report.json

📊 Example Output (JSON)
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

This allows you to immediately see if your VPN setup leaks real identifying information.
