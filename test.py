import subprocess
import re
import ipaddress
import platform
import time

def ping_ip(ip):
    print(f"[>] ping: {ip}")
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        subprocess.run(['ping', param, '1', str(ip)],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[!] ping 실패: {ip} ({e})")

def populate_arp(subnet):
    print(f"[!] IP 대역 스캔 시작: {subnet}")
    for ip in ipaddress.ip_network(subnet).hosts():
        ping_ip(str(ip))
    time.sleep(1)

def find_ip_by_mac(target_mac):
    target_mac = target_mac.lower().replace("-", ":")
    output = subprocess.check_output("arp -a", shell=True).decode()
    for line in output.splitlines():
        if target_mac in line.lower():
            ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
            if ip_match:
                return ip_match.group(0)
    return None

# ✅ 설정
mac_to_find = "98:ba:5f:da:f8:23"   # ← 찾고 싶은 MAC 주소
subnet_range = "192.168.35.0/24"     # ← 본인 네트워크 대역

# 실행
populate_arp(subnet_range)
found_ip = find_ip_by_mac(mac_to_find)

if found_ip:
    print(f"[✓] MAC {mac_to_find} 의 IP 주소는: {found_ip}")
else:
    print(f"[x] MAC {mac_to_find} 에 해당하는 IP를 찾을 수 없습니다.")
