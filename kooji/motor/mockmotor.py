import uasyncio as asyncio
import utime as time
from kooji.primitives.delay_ms import Delay_ms
from random import choice
from kooji.enums import Movement, Position
from kooji.doorsensor import DoorSensor
import logging



# logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
#                     level=logging.INFO,
#                     datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger("MockMotor")
log.setLevel(logging.ERROR)

class MockMotor:
    TRANSITION_TIME_MS = 10000
    DEBOUNCE_MS = 500
    """
    A class used to represent the movement of a toggle start-stop-reverse_start type motor for opening garage doors
    Purpose is to simulate the behaviour to help in the testing of other components
    """
    def __init__(self, door_status_cb=None, current_time_to_open=TRANSITION_TIME_MS, movement=Movement.STOPPED,
                 next_move_direction=Movement.OPENING, loop=None, log_detailed_progress=False, time_to_open=TRANSITION_TIME_MS, debounce_ms=DEBOUNCE_MS):
        """
        Parameters
        ----------

        """
        if not 0 <= current_time_to_open <= time_to_open:
            raise ValueError("current_time_to_open must be between 0 [Closed] and TRANSITION_TIME_MS [Open] inclusive")
        if next_move_direction not in [Movement.CLOSING, Movement.OPENING]:
            raise ValueError("next_move_direction is invalid")
        if (current_time_to_open == 0 and next_move_direction == Movement.OPENING) or (current_time_to_open == time_to_open and next_move_direction == Movement.CLOSING):
            raise ValueError("current_time_to_open and next_move_direction are inconsistent")

        self.__loop = loop
        self.__movement = movement
        self.__next_move_direction = next_move_direction
        self.__transition_time_full_ms = time_to_open
        self.__door_status_cb = door_status_cb
        self.__last_toggle_time = None
        self.__debounce_ms = debounce_ms

        # Initialise __position from based on current_time_to_open
        if current_time_to_open == 0:
            self.__position = Position.OPEN
        elif current_time_to_open == time_to_open:
            self.__position = Position.CLOSED
        else:
            self.__position = Position.PART_OPEN

        # Initialise __transition_time_remaining_ms based on current_time_to_open
        if self.__next_move_direction == Movement.OPENING:
            self.__transition_time_remaining_ms = current_time_to_open
        elif self.__next_move_direction == Movement.CLOSING:
            self.__transition_time_remaining_ms = self.__transition_time_full_ms - current_time_to_open

        self.__transition_timer = None  # Will be set on first move
        self.__log_status('init\t\t')

        if log_detailed_progress:
            self.__loop.create_task(self.log_progress())

        self.__door_status_cb(self.__movement, self.__position)

    @property
    def timer_coro(self):
        return self.__transition_timer._ktask

    @property
    def movement(self):
        return self.__movement

    @property
    def position(self):
        return self.__position

    def toggle(self):
        # Ignore requests that happen within quick succession of first actioned request
        last_toggle_time = self.__last_toggle_time
        if time.ticks_diff(time.ticks_ms(), last_toggle_time) < self.__debounce_ms:  # Debounce repeated requests
            log.info('\ttoggle\t\t\tDebounced toggle request')
            if self.__transition_timer.time_remaining > 0:
                return self.__transition_timer.timer
            else:
                return asyncio.sleep(0)
        else:
            self.__last_toggle_time = time.ticks_ms()

        if self.__movement in [Movement.CLOSING, Movement.OPENING]:
            self.__stop()
            self.__log_status('toggle\t\t')
            return asyncio.sleep(0)
        elif self.__movement == Movement.STOPPED:
            self.__move_to_next_position()
            self.__log_status('toggle\t\t')
            return self.__transition_timer.timer

    def __move_to_next_position(self):
        self.__transition_timer = Delay_ms(self.__movement_complete,
                                           duration=self.__transition_time_remaining_ms)
        self.__transition_timer.trigger()
        # Update movement and position status
        self.__movement = self.__next_move_direction
        self.__position = Position.PART_OPEN
        # Toggle the next move direction
        self.__next_move_direction *= -1
        self.__door_status_cb(self.__movement, self.__position)

    def __stop(self):
        # Grab the remaining time
        tt = self.__transition_timer
        time_remaining = tt.time_remaining
        # Stop the timer and update movement status
        tt.stop()
        self.__movement = Movement.STOPPED
        # Invert the remaining time ready for move in next direction
        self.__transition_time_remaining_ms = self.__transition_time_full_ms - time_remaining
        self.__door_status_cb(self.__movement, self.__position)

    def __movement_complete(self):
        # Replenish remaining time for a full movement and update state
        self.__transition_time_remaining_ms = self.__transition_time_full_ms
        self.__position = self.__movement # Using fact that movements and position have same numeric encoding
        self.__movement = Movement.STOPPED
        self.__next_move_direction *= 1
        self.__log_status('__movement_complete')
        self.__door_status_cb(self.__movement, self.__position)

    def __log_status(self, method):
        log.info(" %s\tPosition: %s | Movement: %s | Next Move Direction: %s", method, Position.description[self.__position], Movement.description[self.__movement], Movement.description[self.__next_move_direction])

    async def log_progress(self):
        # while self.__movement in [Movement.CLOSING,
        #                           Movement.OPENING] and self.__transition_timer.time_remaining is not None:
        while True:
            if self.__movement in [Movement.CLOSING, Movement.OPENING] and self.__transition_timer.time_remaining is not None:
                log.debug(" progress\t\t%s... [%s ms until complete]", Movement.description[self.__movement], str(self.__transition_timer.time_remaining))
            await asyncio.sleep(1)
