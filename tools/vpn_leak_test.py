import requests
import json
import socket
import dns.resolver
import stun

def check_public_ip():
    try:
        return requests.get("https://api.ipify.org?format=json").json()["ip"]
    except:
        return "Error fetching public IP"

def check_dns_leak():
    try:
        resolver = dns.resolver.Resolver()
        return [str(x) for x in resolver.nameservers]
    except:
        return ["Error checking DNS"]

def check_webrtc_leak():
    try:
        nat_type, external_ip, external_port = stun.get_ip_info()
        return {"nat_type": nat_type, "external_ip": external_ip, "external_port": external_port}
    except:
        return {"error": "Could not check WebRTC leak"}

def check_ipv6_leak():
    try:
        ipv6_addr = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6)
        return [ip[4][0] for ip in ipv6_addr]
    except:
        return ["No IPv6 detected"]

def main():
    report = {
        "public_ip": check_public_ip(),
        "dns_leak": check_dns_leak(),
        "webrtc_leak": check_webrtc_leak(),
        "ipv6_leak": check_ipv6_leak()
    }

    with open("vpn_leak_report.json", "w") as f:
        json.dump(report, f, indent=4)

    print("[+] VPN Leak Test complete. Results saved to vpn_leak_report.json")

if __name__ == "__main__":
    main()
