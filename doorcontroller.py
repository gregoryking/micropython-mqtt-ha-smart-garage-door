import machine
import utime
import uasyncio as asyncio
from config import RELAY_PIN, STOP_AND_RETURN_COMMANDS, START_COMMANDS, STOP_COMMANDS, PUSH_BUTTON_PIN, CLOSE_WITH_DELAY_PUSH_BUTTON_TRIGGER_TIME, CLOSE_WITH_DELAY_CLOSE_DELAY
from doorstate import DoorState
from switch import Switch


class DoorController: # pylint: disable=too-few-public-methods
    """DoorController Class

    Class for processing door open and close requests.
    """

    def __init__(self, door_state):
        self.__door_state = door_state
        self.__relay_pin = machine.Pin(RELAY_PIN, machine.Pin.OUT, 0)
        self.__push_button = Switch(PUSH_BUTTON_PIN, True)
        self.__cancel_press_operation = None

        self.__relay_timer = machine.Timer(-1)
        self.__push_button_pressed_time = None
        self.__delayed_close_timer = machine.Timer(-1)
        self.__busy = False

    def update(self):
        # Read values for the manual pushbutton
        irq_state = machine.disable_irq()
        push_button_new_value = self.__push_button.new_value
        machine.enable_irq(irq_state)

        if push_button_new_value is not None:
            self.push_button(push_button_new_value)

    def push_button(self, state):
        if state:
            if self.__door_state.isMoving:
                print("Push button pressed while door known to be moving")
                if self.__busy: # if door is moving because of request DoorController initiated then deinit timer and start a new one
                    self.__relay_timer.deinit()
                    self.__relay_timer = machine.Timer(-1)
                self.__cancel_press_operation = True
                print("Stopping door")
                self._stop
            else:
                print("Push button pressed while door is not known to be moving")
                self.__push_button_pressed_time = utime.ticks_ms()
        if not state:
            if not self.__cancel_press_operation:
                print("Push button depressed - as open or close  operation")
                if self.__door_state == DoorState.CLOSED:
                    self.open()
                if self.__door_state == DoorState.OPEN:
                    if utime.ticks_diff(utime.ticks_ms(), self.__push_button_pressed_time) \
                            > CLOSE_WITH_DELAY_PUSH_BUTTON_TRIGGER_TIME:
                        self._close_with_delay(CLOSE_WITH_DELAY_CLOSE_DELAY)
                    else:
                        self.close()
            else:
                print("Push button depressed - as part of Stop door operation")
                self.__cancel_press_operation = False  # Coming out of cancel operation


    #  TO-DO: Remove code duplication in open/close by genericising?
    def open(self):
        print("Open request received")
        if self.__busy:
            print("Ignoring - still processing a previous request")
            return
        if self.__door_state.status == DoorState.CLOSED:
            print("Triggering open request from a closed state")
            self._start()
            return
        if self.__door_state.status == DoorState.STOPPED:
            print("Triggering open request from a stopped state")
            self._start()
            return
        if self.__door_state.status == DoorState.CLOSING:
            print("Triggering open request from a closING state")    
            self._stop_and_return()
            return
        if self.__door_state.status == DoorState.OPEN:
            print("Ignoring - door already open")
            return
        if self.__door_state.status == DoorState.OPENING:
            print("Ignoring - door in process of opening already")
            return

    def close(self):
        print("Close request received")
        if self.__busy:
            print("Ignoring - still processing a previous request")
            return
        if self.__door_state.status == DoorState.OPEN:
            print("Triggering close request from an open state")
            self._start()
            return
        if self.__door_state.status == DoorState.STOPPED:
            print("Triggering close request from a stopped state")
            self._start()
            return
        if self.__door_state.status == DoorState.OPENING:
            print("Triggering close request from an openING state")    
            self._stop_and_return()
            return
        if self.__door_state.status == DoorState.CLOSED:
            print("Ignoring - door already closed")
            return
        if self.__door_state.status == DoorState.CLOSING:
            print("Ignoring - door in process of closing already")
            return

    # Close after a delay period - if any of the follwoing apply when the request is made or attempts after a delay,
    # it will not perform the close operation:
    #       * Registered busy according to DoorController
    #       * In a position other than CLOSED according to DoorState
    def _close_with_delay(self, delay):
        if self.__busy or self.__door_state != DoorState.CLOSED:
            print("Door not in correct state for a delayed close request, ignoring")
        elif delay > 0:
            self.__delayed_close_timer.init(period=delay, mode=machine.Timer.ONE_SHOT,
                                            callback=self._close_with_delay(0))
        else:
            self.close()

    def toggle(self):
        print("Toggle request received")
        if self.__busy:
            print("Ignoring - still processing a previous request")
            return
        else:
            self.__start()

    def _start(self):
        self.__busy = True
        commands = START_COMMANDS.copy()
        self._process_commands(commands)

    def _stop(self):
        self.__busy = True
        commands = STOP_COMMANDS.copy()
        self._process_commands(commands)

    def _stop_and_return(self):
        self.__busy = True
        commands = STOP_AND_RETURN_COMMANDS.copy()
        self._process_commands(commands)

    # # Recursive processing of commands list, sets __busy to False after processing last command
    # def _process_commands(self, commandList):
    #     if len(commandList) > 0:
    #         command = commandList.pop(0)
    #         self.__relay_pin.value(command['pinLevel'])
    #         print("Processing command: " + str(command))
    #         print (commandList)
    #         self.__relay_timer.init(period=command['duration'], mode=machine.Timer.ONE_SHOT,
    #                                 callback=self._process_commands(commandList))
    #     else:
    #         self.__busy = False

    async def _process_commands(self, commandList):
        print("In _process_commands_async")
        while len(commandList) > 0:
            command = commandList.pop(0)
            print("Processing command: " + str(command))
            self.__relay_pin.value(command['pinLevel'])
            await asyncio.sleep_ms(command['duration'])
            await self._process_commands_async(commandList)
        self.__busy = False
        return




# # TO-DO: Check that deinit'ing a timer that hasn't been initialised won't error.
# self.__door_status_timer.deinit()
