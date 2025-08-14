from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
import socket
import time

class TapoListener(ServiceListener):
    def __init__(self):
        self.devices = []

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            device_name = name.split('.')[0]
            print(f"📡 Found device: {device_name} at {ip}")
            self.devices.append((device_name, ip))

    def update_service(self, zeroconf, type, name):
        pass

def discover_tapo_devices(timeout=5):
    zeroconf = Zeroconf()
    listener = TapoListener()

    print("🔍 Searching for devices...")

    # 시도할 수 있는 서비스 타입
    service_types = [
        "_http._tcp.local.",
        "_tapo._tcp.local.",
        "_ewelink._tcp.local.",
        "_hap._tcp.local.",
        "_tcp.local.",
    ]

    browsers = [ServiceBrowser(zeroconf, service_type, listener) for service_type in service_types]

    try:
        time.sleep(timeout)
    finally:
        zeroconf.close()

    return listener.devices

if __name__ == "__main__":
    devices = discover_tapo_devices()
    if devices:
        print("\n🎯 검색된 장치 목록:")
        for name, ip in devices:
            print(f"- {name} → {ip}")
    else:
        print("❌ 장치를 찾지 못했습니다.")
