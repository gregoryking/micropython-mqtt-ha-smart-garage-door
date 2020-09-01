import uasyncio as asyncio
from machine import Pin
from time import sleep
import sys


class PinTest:
    def __init__(self, test_pin_numbers=[12, 5, 4, 0], mode=Pin.Out):
        self.__mode = mode
        for pin in test_pin_numbers:
            self.__test_pins.append(Pin(pin, mode=mode))

    def run(self):
        if self.__mode == Pin.OUT:
            while True:
                for pin in self.__test_pins:
                    pin.on()
                sys.stdout.write("Switching ALL test pins **ON** \r")
                sleep(2)
                for pin in self.__test_pins:
                    pin.off()
                sys.stdout.write("Switching ALL test pins **OFF**\r")
                sleep(2)
        elif self.__mode == Pin.IN:
            while True:
                for pin in self.__test_pins:
                    sys.stdout.write("{pinDesc}\t{pinValue:01d}\t".format(pinDesc=str(pin), pinValue=pin.value()))
                sys.stdout.write("\r")