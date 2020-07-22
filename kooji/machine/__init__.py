from machine import *
import machine

try:
    machine.Pin
except AttributeError:
    class Pin:
        IN, OUT, PULL_UP, PULL_DOWN = [None, None, None, None]
        @classmethod
        def is_mock(cls):
            pass

        def __init__(self, *args):
            self.__value = None

        def value(self, value=None):
            if value is not None:
                if value not in [1,0]:
                    raise ValueError("Valid pin values are 0 or 1")
                else:
                    self.__value = value
            else:
                return self.__value

        def on(self):
            self.__value = 1

        def off(self):
            self.__value = 0
