import uasyncio as asyncio
from kooji.primitives.switch import Switch
from kooji.machine import Pin, Signal
from config import RELAY_PIN, MOVE_PULSE_DURATION

class Motor:
    def __init__(self):
        self.__relay_signal = Signal(*RELAY_PIN["pinArgs"], invert=RELAY_PIN["inverted"])
        self.__loop = asyncio.get_event_loop()
        print("Using MOVE_PULSE_DURATION of %d", MOVE_PULSE_DURATION)

    async def toggle(self):
        await self.__pulse_coro(MOVE_PULSE_DURATION)

    async def __pulse_coro(self, period):
        self.__relay_signal.on()
        await asyncio.sleep_ms(period)
        self.__relay_signal.off()