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
        self.__stateChangeCallback = state_change_callback

        if (self.__transition_time_total % self.__refresh_ms != 0):
            raise ValueError("refresh_ms must be a factor of transition_duration")

    def door_position(self):
        percentage_closed = self.__transition_time_until_open / self.__transition_time_total
        status = None
        if self.movement == DoorActuator.STOPPED:
            status = DoorActuator.position_labels[self.position]
        else:
            status = DoorActuator.movement_labels[self.movement]
        return "{} ({:.0%})".format(status, percentage_closed)

    def print_status(self):
        log.debug(str(self.proportion_closed) + '\t' + self.door_position())
        # log.debug(self.door_position())

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
        self.print_status()
        # self.__stateChangeCallback({"state": state, "__proportion_closed": self.__proportion_closed})

    # @state.setter
    # def state(self, state):
    #     self.__state = state
    #     self.__stateChangeCallback(state)

    #
    async def move(self):
        log.debug('** move call')
        while True:
            # log.debug('**move iteration pre-debounce**')
            await asyncio.sleep_ms(self.__refresh_ms)
            # log.debug('**move iteration post-debounce**')
            self.__transition_time_until_open -= (self.__movement * self.__refresh_ms)
            if self.__transition_time_until_open % self.__transition_time_total == 0:
                if self.__transition_time_until_open == 0:
                    self.__position = DoorActuator.OPEN
                    self.__next_movement = DoorActuator.CLOSED
                if self.__transition_time_until_open == self.__transition_time_total:
                    self.__position = DoorActuator.CLOSED
                    self.__next_movement = DoorActuator.OPENING
                break
            else:
                self.__position = DoorActuator.PART_OPEN
            self.print_status()

    async def __run(self):
        log.debug("*** __run Call: %s", DoorActuator.position_labels[self.position])

        # await asyncio.sleep_ms(self.__refresh_ms + 50)  # debounce run requests < Refresh rate
        if self.__movement == DoorActuator.OPENING or self.__movement == DoorActuator.CLOSING:
            self.__set_movement(DoorActuator.STOPPED)
        elif self.__movement == DoorActuator.STOPPED:
            if self.__next_movement == DoorActuator.OPENING:
                self.__next_movement = DoorActuator.CLOSING
                self.__set_movement(DoorActuator.OPENING)
            elif self.__next_movement == DoorActuator.CLOSING:
                self.__next_movement = DoorActuator.OPENING
                self.__set_movement(DoorActuator.CLOSING)
            await self.move()
        self.__set_movement(DoorActuator.STOPPED)
        self.__running_task = None

    async def run(self):
        log.debug("*** run Call: %s", DoorActuator.position_labels[self.position])
        log.debug("raw ticks diff is %d", time.ticks_diff(time.ticks_ms(), self.__time_last_run_request))

        # Debounce requests
        lrr = self.__time_last_run_request
        self.__time_last_run_request = time.ticks_ms()
        print("************************* " + str(lrr) + " " + str(self.__time_last_run_request))

        if time.ticks_diff(time.ticks_ms(), lrr) < self.__refresh_ms: # Debounce repeated requests
            log.debug("*** run Debounced a request: %s", DoorActuator.position_labels[self.position])
            self.__time_last_run_request = time.ticks_ms()
            if self.__running_task:
                return await self.__running_task
            else:
                return

        # If no task is currently running, schedule one immediately
        log.debug("***running_task: %s", str(self.__running_task))
        if self.__running_task is None:
            self.__running_task = asyncio.create_task(self.__run())
            return await self.__running_task
        # Else treat a run request as a cancellation
        else:
            log.debug("*** run Cancelling task: %s", DoorActuator.position_labels[self.position])
            self.__running_task.cancel()
            self.__running_task = None
            self.__set_movement(DoorActuator.STOPPED)

#
# def set_global_exception():
#     def handle_exception(loop, context):
#         import sys
#         sys.print_exception(context["exception"])
#         sys.exit()
#     loop = asyncio.get_event_loop()
#     loop.set_exception_handler(handle_exception)
#
#
# async def main():
#     set_global_exception()  # Debug aid
#     myMotor = Motor(lambda x: print('State is ' + str(x)))
#     myMotor2 = Motor(lambda x: print('State2 is ' + str(x)))
#     # asyncio.run(doSomePrinting())
#     # asyncio.create_task(doSomePrinting())
#     # asyncio.create_task(myMotor.run())
#     # asyncio.create_task(myMotor.run())
#     myMotor.run()
#     await asyncio.sleep_ms(11000)
#     myMotor.run()
#     await asyncio.sleep_ms(3000)
#     myMotor.run()
#     await asyncio.sleep_ms(4000)
#     myMotor.run()
#     await asyncio.sleep_ms(4000)
#     myMotor.run()
#     await asyncio.sleep_ms(11000)
#     myMotor.run()
#     await asyncio.sleep_ms(100)
#     myMotor.run()
#     await asyncio.sleep_ms(100)
#     myMotor.run()
#     await asyncio.sleep_ms(100000)
