import uasyncio as asyncio
from kooji.doorsensor import DoorSensor
from kooji.motor.mockmotor import MockMotor
from kooji.mqtt import MQTT
from kooji.enums import Movement, Position
from config import DOOR_STATE_TOPIC, DOOR_TARGET_TOPIC
import logging

log = logging.getLogger("DoorActuator")


class DoorActuator(object):

    @classmethod
    async def create(cls):
        self = DoorActuator()
        self.__loop = asyncio.get_event_loop()
        self.__mqtt = MQTT(subscription_cb=self.subscription_callback)
        await self.__mqtt.connect()

        self.__door_sensor = DoorSensor(door_state_cb=self.door_state, door_target_cb=self.door_target)
        self.__motor = MockMotor(door_status_cb=self.new_door_status, log_detailed_progress=True)

    def door_state(self, status):
        log.info("door_State\t\tPublishing state %s to DOOR_STATE_TOPIC", status)
        pub_msg = self.__mqtt.publish(DOOR_STATE_TOPIC, status)
        self.__loop.create_task(pub_msg)

    def door_target(self, status):
        log.info("door_target\t\tDoing nothing - empty function")

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
            "subscription_callback\t\t\tReceived topic %s with payload %s | The current door_state is %s and movement is %s",
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
        door_position = self.__door_sensor.position
        door_position_str = Position.description[door_position]
        door_movement = self.__door_sensor.movement
        door_movement_str = Movement.description[door_movement]

        # Door already at target position
        if target == door_position and door_movement == Movement.STOPPED:
            log.info("set_target\t Received request to set door target to %s but door is already %s. Ignoring request.",
                     target_str, door_position_str)
            return
        # Door in process of moving to target position
        elif door_movement == target:
            log.info("set_target\t Received request to set door target to %s but door is already in the process of "
                     "%s. Ignoring request.",
                     target_str, door_movement_str)
            return
        # Door in process of moving in opposite direction to target
        pass
        # Door stopped and set to go in wrong direction on next movement
        pass
        # Door stopped and next movement unknown NOTE: Approach that shoudl be taken here is to toggle the motor and
        # get it to a known state. To keep homekit correct, we need to set the target to be in line with status. Test
        # this works okay without ballsing things up
        pass
        # Nothing known about door position or movement
        pass








