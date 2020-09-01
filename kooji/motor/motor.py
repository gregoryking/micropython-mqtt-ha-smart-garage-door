import uasyncio as asyncio
from kooji.primitives.switch import Switch
from kooji.machine import Pin, Signal
from config import RELAY_PIN, MOVE_PULSE_DURATION

class Motor:
    def __init__(self):
        relay_pin = Pin(RELAY_PIN[0], Pin.OUT, RELAY_PIN[1])
        relay_signal = Signal(relay_pin, invert=RELAY_PIN[1])
        self.__relay_switch = Switch(relay_signal)
        self.__loop = asyncio.get_event_loop()

    def toggle(self):
        self.__loop.create_task(self.__pulse_coro(MOVE_PULSE_DURATION))

    async def __pulse_coro(self, period):
        self.__relay_switch.on()
        asyncio.sleep_ms(period)
        self.__relay_switch.off()