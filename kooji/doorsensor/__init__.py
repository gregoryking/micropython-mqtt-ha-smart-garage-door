import uasyncio as asyncio
import utime as time
from config import TRANSITION_DURATION, OPEN_SENSOR_PIN, CLOSED_SENSOR_PIN
import logging
from kooji.machine import Pin
from kooji.primitives.switch import Switch
from kooji.enums import Movement, Position

log = logging.getLogger("DoorSensor")


class DoorSensor:

    def __init__(self):
        # Positions will be updated by switch callbacks
        self.__next_movement = Movement.UNKNOWN
        self.__movement = Movement.UNKNOWN
        self.__position = Position.PART_OPEN

        # Open sensor and callbacks
        self.open_sensor_pin = Pin(OPEN_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        self.open_sensor_pin.off()
        open_switch = Switch(self.open_sensor_pin)
        open_switch.open_func(self.door_opened)  # TO-DO: Had to invert for pin logic on Unix port, check on real port
        open_switch.close_func(self.door_closing) # TO-DO: Had to invert for pin logic on Unix port, check on real port
        # Closed sensor and callbacks
        self.closed_sensor_pin = Pin(CLOSED_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        self.closed_sensor_pin.off()
        closed_switch = Switch(self.closed_sensor_pin)
        closed_switch.open_func(self.door_closed) # TO-DO: Had to invert for pin logic on Unix port, check on real port
        closed_switch.close_func(self.door_opening) # TO-DO: Had to invert for pin logic on Unix port, check on real port

        try:
            Pin.is_mock()
            self.__running_with_pins = False
            log.info("init\t\t\tRunning WITHOUT Pins on simulated hardware")
        except AttributeError:
            self.__running_with_pins = True
            log.info("init\t\t\tRunning WITH Pins on hardware ")

    # TO-DO: Add a setter to movement and position callbacks that publishes mqtt messages

    @property
    def position(self):
        return self.__position

    def door_closed(self):
        log.info("position\t\tDoor Closed")
        self.__movement = Movement.STOPPED
        self.__position = Position.CLOSED
        self.__next_movement = Movement.OPENING

    def door_opened(self):
        log.info("position\t\tDoor Opened")
        self.__movement = Movement.STOPPED
        self.__position = Position.OPEN
        self.__next_movement = Movement.CLOSING

    def door_closing(self):
        log.info("movement\t\tDoor Closing")
        self.__movement = Movement.CLOSING
        self.__position = Position.PART_OPEN

    def door_opening(self):
        log.info("position\t\tDoor Opening")
        self.__movement = Movement.OPENING
        self.__position = Position.PART_OPEN
