from threading import Timer
import mAppDefine
from PyP100 import PyL530 #pip install git+https://github.com/almottier/TapoP100.git@main

class Device():
 
    def __init__(self,name,ip):
        self.name = name
        self.deviceIP = ip
        self.connected = False
        self.lightStatus = False

        self.device = PyL530.L530(ip, mAppDefine.email, mAppDefine.password)

    def connect(self):
        """
        장치 연결 시도 (예: 네트워크 핸드쉐이크).
        실패 시 예외 발생 가능.
        """
        try:
            # 실제 연결 로직은 하위 클래스에서 구현
            self.device.handshake()
            self.device.login()
            self.connected = True
            self.turnOff()
            return (f"[{self.name}][{self.device.address}] 연결 성공")
        except Exception as e:
            self.connected = False
            return (f"[{self.name}][{self.device.address}] 연결 실패 : {e}")
        
    def get_device_info(self,info):
        self.device._get_device_info()[info]
        
    def get_status(self):
        self.device.get_status()

    def set_status(self,status):
        self.device.set_status(status)

    def turnOn(self):
        self.device.turnOn()
        self.lightStatus = True
    
    def turnOff(self):
        self.device.turnOff()
        self.lightStatus = False

    def setBrightness(self,bright):
        self.device.setBrightness(bright)

    def setColorTemp(self,temp):
        self.device.setColorTemp(2700)
    
    def setColor(self,degree,saturation):
        self.device.setColor(degree,saturation) #360도 색상환값, 채도

    def connectTest(self):
        try:
            self.device.turnOff()
            Timer(1.0, self.turnOn).start()
            Timer(2.0, self.turnOff).start()
            Timer(3.0, self.turnOn).start()
            Timer(4.0, self.turnOff).start()

            return (f"[{self.name}][{self.device.address}] 연결 성공")
        except Exception as e:
            return (f"[{self.name}][{self.device.address}] 연결 실패 : {e}")



