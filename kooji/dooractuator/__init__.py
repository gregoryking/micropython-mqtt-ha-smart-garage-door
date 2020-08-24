import uasyncio as asyncio
import utime as time
from kooji.doorsensor import DoorSensor
from kooji.motor.mockmotor import MockMotor
from kooji.mqtt import MQTT
from kooji.enums import Movement, Position
from config import DOOR_STATE_TOPIC, DOOR_TARGET_TOPIC, DEBOUNCE_MS
import logging

log = logging.getLogger("DoorActuator")


class CorrectiveMovement:
    NONE = 0
    IN_PROGRESS = 1
    COMPLETE = 2


class DoorActuator(object):

    @classmethod
    async def create(cls):
        self = DoorActuator()
        self.__loop = asyncio.get_event_loop()
        self.__mqtt = MQTT(subscription_cb=self.subscription_callback)
        await self.__mqtt.connect()

        self.__door_sensor = DoorSensor(door_state_cb=self.door_state, door_target_cb=self.door_target)
        self.__motor = MockMotor(door_status_cb=self.new_door_status, log_detailed_progress=True)

        self.__corrective_movement_task = None
        self.__corrective_movement_status = CorrectiveMovement.NONE

        self.__last_call_time = None

        self.__target = self.__door_sensor.position

    def door_state(self, status):
        log.info("door_state\t\tPublishing state %s to DOOR_STATE_TOPIC", status)
        pub_msg = self.__mqtt.publish(DOOR_STATE_TOPIC, status)
        self.__loop.create_task(pub_msg)

    def door_target(self, status):
        log.info("door_target\t\tPublishing %s to DOOR_TARGET_TOPIC", status)
        pub_msg = self.__mqtt.publish(DOOR_TARGET_TOPIC, status)
        self.__loop.create_task(pub_msg)

    # When using mock motor, have mock motor change the sensor pins to simulate motor movement.
    def new_door_status(self, movement, position):
        log.info("new_door_status\t\tNew door status received from mock motor, switches being updated accordingly")
        if position == Position.CLOSED:
            self.__door_sensor.closed_sensor_pin.on()
        elif position == Position.OPEN:
            self.__door_sensor.open_sensor_pin.on()

        if movement == Movement.OPENING:
            self.__door_sensor.closed_sensor_pin.off()
        elif movement == Movement.CLOSING:
            self.__door_sensor.open_sensor_pin.off()


    # def set_door_tartget(self, target):
    #     log.info("Received target %s adn current door state is %s", str(target), str(self.__door_sensor.position))

    def subscription_callback(self, topic, msg_str, retained):
        msg_str = msg_str.decode('utf-8')
        topic_str = topic.decode('utf-8')
        current_door_position = Position.description[self.__door_sensor.position]
        current_door_movement = Movement.description[self.__door_sensor.movement]
        log.info(
            "subscription_callback\tReceived topic %s with payload %s | The current door_state is %s and movement is %s",
            topic_str, msg_str, current_door_position, current_door_movement)
        if topic_str == DOOR_TARGET_TOPIC and retained is False: # TO-DO: Revisit wheteher retained should be ignored - may actually be desirable to action based on retained messages that had been missed
            # self.toggle()
            target_position = [key for key, value in Position.description.items() if value == msg_str][0]
            self.set_target(target_position)

    # if topic == DOOR_TARGET_TOPIC.encode('utf-8') and retained is False:
    #     set_target(msg_str)
    def toggle(self):
        self.__motor.toggle()

    def set_target(self, target):
        target_str = Position.description[target]
        self_target_str = Position.description[self.__target]
        last_call_time = self.__last_call_time
        elapsed_since_last_processed_call = time.ticks_diff(time.ticks_ms(), last_call_time)

        # Disregard requests whose target state is already being actioned, happen too soon after a prior request or may interfere with already running slow running corrective
        # requests
        if self.__target == target:
            log.info("set_target\t\tReceived request to set door target to %s, ignoring as already know I'm aiming "
                     "for %s", target_str, self_target_str)
            return
        elif elapsed_since_last_processed_call < DEBOUNCE_MS:  # Debounce repeated requests
            log.info("set_target\t\tReceived request to set door target to %s, ignoring as only %d ms have passed "
                     "since last call processing began. Debouncing threshold set to %d ms "
                     , target_str, elapsed_since_last_processed_call, DEBOUNCE_MS)
            self.door_target(self_target_str)
            return
        elif self.__corrective_movement_status == CorrectiveMovement.IN_PROGRESS:
            log.info("set_target\t\tCorrective movement in progress to %s, ignoring request to set target to %s and "
                     "resetting target state to %s", self_target_str, target_str,  self_target_str)
            self.door_target(self_target_str)
            return

        door_position = self.__door_sensor.position
        door_position_str = Position.description[door_position]
        door_movement = self.__door_sensor.movement
        door_movement_str = Movement.description[door_movement]
        door_next_movement = self.__door_sensor.next_movement
        door_next_movement_str = Movement.description[door_next_movement]

        # Update door actuator with the target it is aiming for.
        self.__target = target

        # Record the last time a call was considered for processing (used by debouncing logic above)
        self.__last_call_time = time.ticks_ms()

        # Door already at target position
        if target == door_position and door_movement == Movement.STOPPED:
            log.info("set_target\t\tReceived request to set door target to %s but door is already %s. Ignoring request.",
                     target_str, door_position_str)
        # Door in process of moving to target position
        elif door_movement == target:
            log.info("set_target\t\tReceived request to set door target to %s but door is already in the process of "
                     "%s. Ignoring request.",
                     target_str, door_movement_str)
        # Door Stopped at opposite position and ready to go
        elif door_position * -1  == target and door_movement == Movement.STOPPED:
            self.__motor.toggle()
        # WARNING: should think really carefully about 'clever' stuff that might involve start/stops to return that
        # may get door to desired target position during move.  Think about external factors and fallback. Above all
        # ensure does not result in endless cycling
        #
        # Door in process of moving in opposite direction to target
        elif door_movement == target * -1 and door_position == Position.PART_OPEN:
            log.info("set_target\t\tReceived request to set door target to %s, but door is currently %s. Calling __stop_and_return",
                     target_str, door_movement_str)
            self.__corrective_movement_task = self.__loop.create_task(self.__stop_and_return())
            # TO-DO: Add task running check to beginning of set_target which cancels if it exists and is running.
        # Door stopped, part_open and set to go in right direction on next movement
        elif door_movement == Movement.STOPPED and door_position == Position.PART_OPEN and target == door_next_movement:
            log.info("set_target\t\tReceived request to set door target to %s. Door is currently %s, requesting %s of door",
                     target_str, door_movement_str, door_next_movement_str)
            self.__motor.toggle()
        # Door stopped, part_open and set to go in wrong direction on next movement
        elif door_movement == Movement.STOPPED and door_position == Position.PART_OPEN and target == door_next_movement * -1:
            log.info("set_target\t\tReceived request to set door target to %s, but door is currently %s and next movement is set to be %s. Calling __start_stop_and_return",
                     target_str, door_movement_str, door_next_movement_str)
            self.__corrective_movement_task = self.__loop.create_task(self.__start_stop_and_return())
        # Door stopped, part_open and next movement unknown
        elif door_movement == Movement.STOPPED and door_position == Position.PART_OPEN and door_next_movement == Movement.UNKNOWN:
            log.info(
                "set_target\t\tReceived request to set door target to %s, door is currently %s, %s and next movement is %s.",
                target_str, door_movement_str, door_position_str, door_next_movement_str)
            self.__motor.toggle()
            # TO-DO: Approach that taken here thus far is to toggle the motor to get it to a known state. To keep
            # homekit correct, we need to set the target to be in line with status. Need to work out how to do this
            # ensuring it doesn't balls things up (eg by keeping retriggering set_target operations as a result.
            # Potential approach could be to call set_target whenever it reaches Closed or Open position having
            # previously had unknown next_movement? Possible okay because on next call set_target will ignore because
            # it knows it got to the right place, but is it a bit spammy on the mqtt??
        # Does this condition ever trigger? Error log if it does so we can work out what to do with it
        else:
            log.error(
                "set_target\t\tEncoutnered an unknown condition where target: %s | door_movement: %s | door_position: %s | next_movement: %s",
                target_str, door_movement_str, door_position_str, door_next_movement_str)

    async def __stop_and_return(self):
        self.__corrective_movement_status = CorrectiveMovement.IN_PROGRESS
        log.info("__stop_and_return\tStopping the door")
        self.__motor.toggle()
        self.__door_sensor.door_stopped_while_moving()
        await asyncio.sleep(1)
        log.info("__stop_and_return\t %s the door", Movement.description[self.__door_sensor.next_movement])
        self.__motor.toggle()
        self.__door_sensor.door_started_while_stopped()
        await asyncio.sleep(1)
        self.__corrective_movement_status = CorrectiveMovement.COMPLETE


    async def __start_stop_and_return(self):
        self.__corrective_movement_status = CorrectiveMovement.IN_PROGRESS
        log.info("__start_stop_and_return\t%s the door", Movement.description[self.__door_sensor.next_movement])
        self.__motor.toggle()
        self.__door_sensor.door_started_while_stopped()
        await asyncio.sleep(1)
        if self.__door_sensor.position == Position.PART_OPEN and self.__door_sensor.movement in [Movement.CLOSING, Movement.OPENING]: # This part made consitional as stop is not required if that start move in wrong direction gets there and stops of its own accord (eg it is really close to reachign wrong direction)
            log.info("__start_stop_and_return\tStopping the door")
            self.__motor.toggle()
            self.__door_sensor.door_stopped_while_moving()
            await asyncio.sleep(1)
        log.info("__start_stop_and_return\t%s the door", Movement.description[self.__door_sensor.next_movement])
        self.__motor.toggle()
        self.__door_sensor.door_started_while_stopped()
        await asyncio.sleep(1)
        self.__corrective_movement_status = CorrectiveMovement.COMPLETE
