def unique_id(): return b'\xbe\xef\xf0\x0d'

class __interface:
    def __init__(self): self.connected = False
    def connect(self, ssid, pwd, listen_interval=3): self.connected = True
    def disconnect(self): self.connected = False
    def isconnected(self): return self.connected
    def active(self, on): pass
    def status(self): return 1
class network:
    def WLAN(self):
        return network.STA_IF

    STAT_CONNECTING = 2
    STA_IF = __interface()