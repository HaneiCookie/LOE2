from threading import Timer, Thread, Event, RLock
import time, random
import mAppDefine
from PyP100 import PyL530  # pip install git+https://github.com/almottier/TapoP100.git@main

class Device():
    def __init__(self, name, ip):
        self.name = name
        self.deviceIP = ip
        self.connected = False
        self.lightStatus = False

        self.device = PyL530.L530(ip, mAppDefine.email, mAppDefine.password)

        # --- Keep-alive용 내부 상태 ---
        self._ka_thread = None
        self._ka_stop = Event()
        self._lock = RLock()
        self._last_ok = 0.0            # 마지막 성공 시각(monotonic)
        self._STALE_SEC = 40           # 이 시간 이상 지나면 명령 전 신선도 확보
        self._KA_INTERVAL = 45         # 주기(초). 여러 대면 ±지터로 분산

    # ---------------- 기본 연결/제어 ----------------
    def connect(self):
        try:
            self.device.handshake()
            self.device.login()
            self.connected = True
            self._last_ok = time.monotonic()
            self.turnOff()
            return (f"[{self.name}][{self.device.address}] 연결 성공")
        except Exception as e:
            self.connected = False
            return (f"[{self.name}][{self.device.address}] 연결 실패 : {e}")

    def get_device_info(self, info):
        # 원래 코드에 return이 빠져 있었음(작동 위해 반환 추가)
        return self.device._get_device_info()[info]

    def get_status(self):
        return self.device.get_status()

    def set_status(self, status):
        self._ensure_fresh()
        self.device.set_status(status)

    def turnOn(self):
        self._ensure_fresh()
        self.device.turnOn()
        self.lightStatus = True

    def turnOff(self):
        self._ensure_fresh()
        self.device.turnOff()
        self.lightStatus = False

    def setBrightness(self, bright):
        self._ensure_fresh()
        self.device.setBrightness(bright)

    def setColorTemp(self, temp):
        self._ensure_fresh()
        self.device.setColorTemp(temp)

    def setColor(self, degree, saturation):
        self._ensure_fresh()
        self.device.setColor(degree, saturation)  # 0~360, 0~100

    def connectTest(self):
        try:
            self.turnOff()
            Timer(1.0, self.turnOn).start()
            Timer(2.0, self.turnOff).start()
            Timer(3.0, self.turnOn).start()
            Timer(4.0, self.turnOff).start()
            return (f"[{self.name}][{self.device.address}] 연결 성공")
        except Exception as e:
            return (f"[{self.name}][{self.device.address}] 연결 실패 : {e}")

    # ---------------- 세션 유지(keep-alive) ----------------
    def start_keepalive(self, interval_sec: int | None = None):
        """백그라운드로 세션 유지 시작"""
        with self._lock:
            if self._ka_thread and self._ka_thread.is_alive():
                return  # 이미 동작 중
            if interval_sec is not None:
                self._KA_INTERVAL = max(10, int(interval_sec))
            self._ka_stop.clear()
            self._ka_thread = Thread(target=self._keepalive_loop, name=f"KA-{self.name}", daemon=True)
            self._ka_thread.start()

    def stop_keepalive(self):
        """세션 유지 중지"""
        with self._lock:
            if not self._ka_thread:
                return
            self._ka_stop.set()
        # join은 락 밖에서
        self._ka_thread.join(timeout=2.0)

    # ---------------- 내부 유틸 ----------------
    def _probe(self):
        """
        가벼운 상태 조회로 세션 확인.
        성공하면 self._last_ok 갱신.
        """
        # 라이브러리 별로 get_status() 또는 _get_device_info()가 가볍다.
        self.device.get_status()
        self._last_ok = time.monotonic()

    def _reconnect(self):
        """세션 재수립: handshake + login"""
        self.device.handshake()
        self.device.login()
        self.connected = True
        self._last_ok = time.monotonic()

    def _ensure_fresh(self):
        """
        명령 직전에 신선도 보장:
        - STALE_SEC 초 이상 지나면 probe 시도
        - 실패 시 재핸드셰이크 후 재시도
        """
        now = time.monotonic()
        if now - self._last_ok <= self._STALE_SEC:
            return
        with self._lock:
            try:
                self._probe()
            except Exception:
                # 세션 만료/네트워크 이슈 → 재연결
                self._reconnect()

    def _keepalive_loop(self):
        """
        백그라운드 스레드:
        - 주기적으로 probe()
        - 실패 시 즉시 재연결
        - ±5초 지터로 여러 디바이스 동시 호출 분산
        """
        # 시작 시 한 번 보수적 확인
        with self._lock:
            try:
                if not self.connected:
                    self._reconnect()
                else:
                    self._probe()
            except Exception:
                try:
                    self._reconnect()
                except Exception:
                    pass

        while not self._ka_stop.is_set():
            # 지터 포함 슬립
            jitter = random.uniform(-5, 5)
            wait_s = max(10, self._KA_INTERVAL + jitter)
            # 이벤트가 set되면 일찍 깨어남
            if self._ka_stop.wait(timeout=wait_s):
                break

            # 주기적 점검
            with self._lock:
                try:
                    self._probe()
                except Exception:
                    try:
                        self._reconnect()
                    except Exception:
                        # 다음 루프에서 재시도
                        pass
