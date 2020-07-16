import uasyncio as asyncio
import utime as time
from config import TRANSITION_DURATION
import logging

log = logging.getLogger("motor")
log.setLevel(logging.DEBUG)


class DoorActuator:
    # DOOR MOVEMENT
    CLOSING = -1
    STOPPED = 0
    OPENING = 1

    # DOOR POSITION
    CLOSED = -1
    PART_OPEN = 0
    OPEN = 1
    UNKNOWN = 2

    movement_labels = {-1: "Closing",
                       0: "Stopped",
                       1: "Opening"}

    position_labels = {-1: "Closed",
                       0: "Part Open",
                       1: "Open",
                       2: "Unknown"}

    default_transition_time_total = TRANSITION_DURATION

    def __init__(self, transition_duration=default_transition_time_total, refresh_ms=200, state_change_callback=None):
        self.__next_movement = DoorActuator.OPENING
        self.__movement = DoorActuator.STOPPED
        self.__position = DoorActuator.CLOSED
        self.__transition_time_total = transition_duration
        self.__refresh_ms = refresh_ms
        self.__transition_time_until_open = transition_duration
        self.__time_last_run_request = None
        self.__running_task = None
        self.__stateChangeCallback = state_change_callback # unused at present

        if self.__transition_time_total % self.__refresh_ms != 0:
            raise ValueError("refresh_ms must be a factor of transition_duration")

    def door_position(self):
        percentage_closed = self.__transition_time_until_open / self.__transition_time_total
        status = None
        if self.movement == DoorActuator.STOPPED:
            status = DoorActuator.position_labels[self.position]
        else:
            status = DoorActuator.movement_labels[self.movement]
        return "{} ({:.0%})".format(status, percentage_closed)

    def print_status(self, level=logging.DEBUG):
        log.log(level, "\tstatus\t%s", self.door_position())

    @property
    def position(self):
        return self.__position;

    @property
    def movement(self):
        return self.__movement

    @property
    def status(self):
        pass

    @property
    def transition_time_total(self):
        return self.__transition_time_total

    @property
    def state(self):
        return self.__movement

    @property
    def proportion_closed(self):
        return self.__transition_time_until_open

    def __set_movement(self, state):
        self.__movement = state
        # self.print_status()

    # @state.setter
    # def state(self, state):
    #     self.__state = state
    #     self.__stateChangeCallback(state)

    #
    async def move(self):
        log.info("\tmove\tStarting door movement")
        self.print_status(logging.INFO)
        while True:
            await asyncio.sleep_ms(self.__refresh_ms)
            self.__transition_time_until_open -= (self.__movement * self.__refresh_ms)
            self.update_position()
            if self.__position != DoorActuator.PART_OPEN:
                self.__movement = DoorActuator.STOPPED
                log.info("\tmove\tEnding door movement")
                self.print_status(logging.INFO)
                break

    def update_position(self):
        if self.__transition_time_until_open % self.__transition_time_total == 0:
            if self.__transition_time_until_open == 0:
                self.__position = DoorActuator.OPEN
                self.__next_movement = DoorActuator.CLOSED
            if self.__transition_time_until_open == self.__transition_time_total:
                self.__position = DoorActuator.CLOSED
                self.__next_movement = DoorActuator.OPENING
        else:
            self.__position = DoorActuator.PART_OPEN

    async def run(self):
        log.info("\trun\tProcessing run request from [%s] position and [%s] movement state",
                  DoorActuator.position_labels[self.position],
                  DoorActuator.movement_labels[self.movement])

        # Debounce requests
        lrr = self.__time_last_run_request
        self.__time_last_run_request = time.ticks_ms()
        if time.ticks_diff(time.ticks_ms(), lrr) < self.__refresh_ms: # Debounce repeated requests
            log.info("\trun\tDebounced run request from [%s] position and [%s] movement state",
                      DoorActuator.position_labels[self.position],
                      DoorActuator.movement_labels[self.movement])
            self.__time_last_run_request = time.ticks_ms()
            if self.__running_task:
                return await self.__running_task
            else:
                return

        # If no task is currently running, schedule one immediately
        if self.__running_task is None:
            log.info("\trun\t%s", "Scheduling a new move task")
            self.__set_movement(self.__next_movement)
            self.__next_movement *= -1
            self.__running_task = asyncio.create_task(self.move())
            await self.__running_task
            self.__set_movement(DoorActuator.STOPPED)
            self.__running_task = None

        # Else treat a run request as a cancellation
        else:
            log.info("\trun\t Cancelling [%s] operation", DoorActuator.movement_labels[self.movement])
            self.__running_task.cancel()
            self.__running_task = None
            self.__set_movement(DoorActuator.STOPPED)
            self.print_status()


#
# def set_global_exception():
#     def handle_exception(loop, context):
#         import sys
#         sys.print_exception(context["exception"])
#         sys.exit()
#     loop = asyncio.get_event_loop()
#     loop.set_exception_handler(handle_exception)
