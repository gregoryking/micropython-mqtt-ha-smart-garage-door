import machine
from config import TRANSITION_DURATION, STATE_TOPIC

class DoorState(): # pylint: disable=too-few-public-methods
    """DoorState Class

    Class for tracking and reporting the state of a door.
    Uses a timer to infer the door has stopped if it hasn't reach an open/closed
    state within TRANSITION_DURATION
    """
    STOPPED, OPEN, OPENING, CLOSED, CLOSING = 0, 1, 2, 3, 4

    def __init__(self, open_reed_switch, closed_reed_switch, client):
        self.__door_status_timer = machine.Timer(-1)
        self.__open_reed_switch = open_reed_switch
        self.__closed_reed_switch = closed_reed_switch
        self.__client = client
        self.moving = False

    def start_door_transition(self):
        self.moving = True
        self.__door_status_timer.init(period=TRANSITION_DURATION, mode=machine.Timer.ONE_SHOT,
                                    callback=self._door_transition_check)

    def end_door_transition(self):
        self.moving = False
        # TO-DO: Check that deinit'ing a timer that hasn't been initialised won't error.
        self.__door_status_timer.deinit()

    def _door_transition_check(self, _):
        # Disable interrupts for a short time to read shared variable
        irq_state = machine.disable_irq()
        open_reed_switch_value = not self.__open_reed_switch.value
        closed_reed_switch_value = not self.__closed_reed_switch.value
        machine.enable_irq(irq_state)

        if (not open_reed_switch_value and not closed_reed_switch_value):
            self.__client.publish(STATE_TOPIC, "Stopped")