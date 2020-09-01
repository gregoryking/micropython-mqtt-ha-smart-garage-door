import uasyncio as asyncio
from kooji.machine import Pin, Signal
from kooji.primitives.pushbutton import Pushbutton
from config import PUSH_BUTTON_PIN
import logging

log = logging.getLogger("DoorButton")

class PushButtonLifecycle:
    NONE = 0
    DEPRESSED = 1
    DEPRESSED_AND_CAUSED_STOP =2
    DEPRESSED_LONG_AND_CAUSED_STOP = 3
    DEPRESSED_LONG = 4
    RELEASED = 5

class DoorButton:
    def __init__(self, door_sensor, toggle_cb):
        self.__loop = asyncio.get_event_loop()
        self.__push_button_signal = Signal(Pin(PUSH_BUTTON_PIN[0], Pin.IN, PUSH_BUTTON_PIN[1]), invert=PUSH_BUTTON_PIN[1])
        self.__push_button = Pushbutton(self.__push_button_signal) # TODO: Check that PULL_UP is indeed correct for this pin
        self.__push_button.press_func(self.__push_button_down)
        self.__push_button.long_func(self.__push_button_long_press_detected)
        self.__push_button.release_func(self.__push_button_up)
        self.__push_button_lifecycle = PushButtonLifecycle.NONE
        self.__door_sensor = door_sensor
        self.__toggle_cb = toggle_cb
        self.__long_press_task = None

    @property
    def push_button_signal(self):
        return self.__push_button_signal

    def __push_button_down(self):
        self.__push_button_lifecycle = PushButtonLifecycle.DEPRESSED
        if self.__door_sensor.moving:
            log.info("__push_button_down\tDoor moving, toggling motor to stop movement now")
            self.__push_button_lifecycle = PushButtonLifecycle.DEPRESSED_AND_CAUSED_STOP
            self.__loop.create_task(self.__toggle_cb(toggle_type="stop"))
        # TODO: See if we want to capture a previous long press so when a long press is detected while a delayed open is running, it cancels the long running.


    def __push_button_long_press_detected(self):
        if self.__push_button_lifecycle == PushButtonLifecycle.DEPRESSED_AND_CAUSED_STOP:
            self.__push_button_lifecycle = PushButtonLifecycle.DEPRESSED_LONG_AND_CAUSED_STOP
        else:
            self.__push_button_lifecycle = PushButtonLifecycle.DEPRESSED_LONG

    def __push_button_up(self):
        if self.__push_button_lifecycle in [PushButtonLifecycle.DEPRESSED_AND_CAUSED_STOP, PushButtonLifecycle.DEPRESSED_LONG_AND_CAUSED_STOP]:
            pass # Don't do anthing on button up when the down caused a stop
        elif not self.__door_sensor.moving: # Only cause a toggle when door is not moving as the result of some other another action
            try:
                self.__long_press_task.cancel()
            except AttributeError:
                log.info("__push_button_up\tThere was no __long_press_task to cancel")
            else:
                log.info("__push_button_up\t__long_press_task was cancelled")

            if self.__push_button_lifecycle == PushButtonLifecycle.DEPRESSED:
                log.info("__push_button_up\tShort press release detected, toggling motor")
                # self.__loop.create_task(self.__toggle_cb())
                self.__loop.create_task(self.__toggle_cb(toggle_type="start"))
            elif self.__push_button_lifecycle == PushButtonLifecycle.DEPRESSED_LONG and not self.__door_sensor.moving:
                log.info("__push_button_up\tLong press release detected, toggling motor after a delay")
                self.__long_press_task = self.__loop.create_task(self.__toggle_cb(toggle_type="start", delay=10))
        self.__push_button_lifecycle = PushButtonLifecycle.RELEASED

    # Methods to assist UNIX port testing of button behaviours (called via mqtt in dooractuator)
    async def simulate_short_button_press(self):
        self.__push_button_signal.on()
        await asyncio.sleep_ms(300)
        self.__push_button_signal.off()
        return

    async def simulate_long_button_press(self):
        log.info("simulate_long_button_press\tSimulating long button press")
        self.__push_button_signal.on()
        await asyncio.sleep_ms(1200)
        self.__push_button_signal.off()
        return
