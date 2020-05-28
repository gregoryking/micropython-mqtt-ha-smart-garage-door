import machine


class Switch:  # pylint: disable=too-few-public-methods
    """Switch Class

    Class for defining a switch. Uses internal state to debounce switch in
    software. To use switch, check the "new_value_available" member and the
    "value" member from the application.
    """
    def __init__(self, pin, inverted = False):
        self.__inverted = inverted
        self.__pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.__pin.irq(handler=self._switch_change,
                       trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING)

        self.__debounce_timer = machine.Timer(-1)
        self.__new_value_available = False
        self.__value = self.__pin.value()
        self.__prev_value = self.__value 
        self.__debounce_checks = 0

    # Returns the current value for the switch
    @property
    def value(self):
        return not self.__value if self.__inverted else self.__value

    # Returns None if the value hasn't changed since the last time it was read,
    # else returns the 'newValue' for the switch
    @property
    def new_value(self):
        if self.__new_value_available:
            self.__new_value_available = False 
            return self.value # TO-DO: Check property can be accessed in class like this. If not replicat logic
        else:
            return None

    def _switch_change(self, pin):
        self.__value =  self.__pin.value()

        # Start timer to check for debounce
        self.__debounce_checks = 0
        self._start_debounce_timer()

        # Disable IRQs for GPIO pin while debouncing
        self.__pin.irq(trigger=0)

    def _start_debounce_timer(self):
        self.__debounce_timer.init(period=100, mode=machine.Timer.ONE_SHOT,
                                   callback=self._check_debounce)

    def _check_debounce(self, _):
        new_value = self.__pin.value()

        if new_value == self.__value:
            self.__debounce_checks = self.__debounce_checks + 1

            if self.__debounce_checks == 3:
                # Values are the same, debouncing done

                # Check if this is actually a new value for the application
                if self.__prev_value != self.__value:
                    self.__new_value_available = True
                    self.__prev_value = self.__value

                # Re-enable the Switch IRQ to get the next change
                self.__pin.irq(handler=self._switch_change,
                               trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING)
            else:
                # Start the timer over to make sure debounce value stays the same
                self._start_debounce_timer()
        else:
            # Values are not the same, update value we're checking for and
            # delay again
            self.__debounce_checks = 0
            self.__value = new_value
            self._start_debounce_timer()
