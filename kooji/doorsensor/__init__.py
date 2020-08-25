import uasyncio as asyncio
import utime as time
from config import OPEN_SENSOR_PIN, CLOSED_SENSOR_PIN
import logging
from kooji.machine import Pin
from kooji.primitives.switch import Switch
from kooji.enums import Movement, Position


log = logging.getLogger("DoorSensor")


class DoorSensor:

    def __init__(self, door_state_cb, door_target_cb):
        # Positions will be updated by switch callbacks
        self.__next_movement = Movement.UNKNOWN
        self.__movement = Movement.UNKNOWN
        self.__position = Position.UNKNOWN

        # Open sensor and callbacks
        self.open_sensor_pin = Pin(OPEN_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        self.open_sensor_pin.off()
        open_switch = Switch(self.open_sensor_pin)
        open_switch.open_func(self.__door_opened)  # TO-DO: Had to invert for pin logic on Unix port, check on real port
        open_switch.close_func(self.__door_closing) # TO-DO: Had to invert for pin logic on Unix port, check on real port
        # Closed sensor and callbacks
        self.closed_sensor_pin = Pin(CLOSED_SENSOR_PIN, Pin.IN, Pin.PULL_UP)
        self.closed_sensor_pin.off()
        closed_switch = Switch(self.closed_sensor_pin)
        closed_switch.open_func(self.__door_closed) # TO-DO: Had to invert for pin logic on Unix port, check on real port
        closed_switch.close_func(self.__door_opening) # TO-DO: Had to invert for pin logic on Unix port, check on real port

        self.__door_state_cb = door_state_cb
        self.__door_target_cb = door_target_cb

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

    @property
    def movement(self):
        return self.__movement

    @property
    def moving(self):
        return self.__movement in [Movement.CLOSING, Movement.OPENING]

    @property
    def next_movement(self):
        return self.__next_movement

    def __door_closed(self):
        log.info("position\t\tDoor Closed")
        if self.__movement != Movement.CLOSING: # If didn't arrive here via a known closing movement, set correct target
            self.__door_target_cb("Closed")
        self.__movement = Movement.STOPPED
        self.__position = Position.CLOSED
        self.__next_movement = Movement.OPENING
        self.__door_state_cb("Closed")

    # Movements derived from sensors

    def __door_opened(self):
        log.info("position\t\tDoor Opened")
        if self.__movement != Movement.OPENING: # If didn't arrive here via a known closing movement, set correct target
            self.__door_target_cb("Open")
        self.__movement = Movement.STOPPED
        self.__position = Position.OPEN
        self.__next_movement = Movement.CLOSING
        # self.__door_target_cb("Open")
        self.__door_state_cb("Open")

    def __door_closing(self):
        log.info("movement\t\tDoor Closing")
        self.__movement = Movement.CLOSING
        self.__position = Position.PART_OPEN
        self.__door_target_cb("Closed")
        self.__door_state_cb("Closing")

    # noinspection MicroPythonRequirements
    def __door_opening(self):
        log.info("position\t\tDoor Opening")
        self.__movement = Movement.OPENING
        self.__position = Position.PART_OPEN
        self.__door_target_cb("Open")
        self.__door_state_cb("Opening")

    # Movements NOT derived from sensors - can be called by instances of DoorSensor

    def door_stopped_while_moving(self):
        log.info("position\t\tDoor Stopped")
        self.__movement = Movement.STOPPED
        self.__next_movement *= -1
        self.__position = Position.PART_OPEN
        self.__door_state_cb("Stopped")

    def door_started_while_stopped(self):
        if self.__next_movement == Movement.CLOSING:
            self.__door_closing()
        elif self.__next_movement == Movement.OPENING:
            self.__door_opening()