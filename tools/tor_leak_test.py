import requests, socket, json

TOR_PROXY = "socks5h://127.0.0.1:9050"

def check_ip(proxy=None):
    try:
        r = requests.get("https://check.torproject.org/api/ip", proxies=proxy, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def dns_leak_test():
    try:
        # Try resolving google.com without proxy (local resolver)
        ip_local = socket.gethostbyname("google.com")
        # Resolve through Tor proxy
        proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
        ip_tor = requests.get("https://dns.google/resolve?name=google.com", proxies=proxies).json()
        return {"dns_local": ip_local, "dns_tor": ip_tor.get("Answer", [{}])[0].get("data")}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    proxies = {"http": TOR_PROXY, "https": TOR_PROXY}

    report = {
        "ip_check": check_ip(proxies),
        "dns_check": dns_leak_test(),
    }

    with open("tor_leak_report.json", "w") as f:
        json.dump(report, f, indent=4)

    print("[+] Leak test complete. Results saved to tor_leak_report.json")
