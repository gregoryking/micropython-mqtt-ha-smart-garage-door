import uasyncio as asyncio
from kooji.primitives.switch import Switch
from kooji.machine import Pin
from config import RELAY_PIN, MOVE_PULSE_DURATION, STOP_PULSE_DURATION

class Motor:
    def __init__(self):
        self.__relay_switch = Switch(Pin(RELAY_PIN, Pin.OUT, Pin.PULL_UP)) # TODO: Check that PULL_UP is indeed correct for this pin
        self.__loop = asyncio.get_event_loop()

    def toggle(self):
        self.__loop.create_task(self.__pulse_coro(MOVE_PULSE_DURATION))

    async def __pulse_coro(self, period):
        self.__relay_switch.on()
        asyncio.sleep_ms(period)
        self.__relay_switch.off()