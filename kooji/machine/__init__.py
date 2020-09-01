from machine import *
import machine

try:
    machine.Pin
except AttributeError:
    class Pin:
        IN, OUT, PULL_UP, PULL_DOWN = [None, None, 1, None]
        @classmethod
        def is_mock(cls):
            pass

        def __init__(self, id, mode=-1, pull=False):
            self.__pull = pull
            self.__value = 0 ^ pull # Changed to handle sensing in Pushbutton

        def value(self, value=None):
            if value is not None:
                if value not in [1, 0]:
                    raise ValueError("Valid pin values are 0 or 1")
                else:
                    self.__value = value
            else:
                return self.__value

        def on(self):
            self.__value = 1 ^ self.__pull

        def off(self):
            self.__value = 0 ^ self.__pull

    class Signal:
        def __init__(self, pin, invert=False):
            self.__pin = pin
            self.__invert = invert

        def value(self, val=None):
            if val is not None:
                self.__pin.value(val ^ self.__invert)
            else:
                return self.__pin.value() ^ self.__invert

        def on(self):
            self.__pin.value(1 ^ self.__invert)

        def off(self):
            self.__pin.value(0 ^ self.__invert)
