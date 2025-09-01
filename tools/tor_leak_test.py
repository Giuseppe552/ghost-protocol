import json
import socket
import requests

TOR = "socks5h://127.0.0.1:9050"
PROX = {"http": TOR, "https": TOR}


def check_ip():
    try:
        r = requests.get("https://check.torproject.org/api/ip", proxies=PROX, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def dns_leak_test():
    try:
        local = socket.gethostbyname("example.com")
        r = requests.get("https://dns.google/resolve?name=example.com", proxies=PROX, timeout=10)
        tor_ans = r.json().get("Answer", [{}])[0].get("data")
        return {"dns_local": local, "dns_via_tor": tor_ans}
    except Exception as e:
        return {"error": str(e)}


def main():
    report = {"ip_check": check_ip(), "dns_check": dns_leak_test()}
    with open("tor_leak_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("[+] Leak test complete -> tor_leak_report.json")


if __name__ == "__main__":
    main()
