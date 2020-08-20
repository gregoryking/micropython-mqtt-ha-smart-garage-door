import uasyncio as asyncio
import time
from kooji.primitives.delay_ms import Delay_ms
from kooji.motor.mockmotor import MockMotor
from kooji.doorsensor import DoorSensor
from kooji.enums import Movement, Position
from mqtt_as import MQTTClient
from config_mqtt import config
from config import SERVER, DOOR_TARGET_TOPIC, DOOR_STATE_TOPIC, COMMAND_TOPIC
import logging

log = logging.getLogger("HackyTest")


loop = asyncio.get_event_loop()

# Task running
async def execute_and_wait(coro, wait):
    if wait is None:
        await coro()
    elif wait == 0:
        coro()
    else:
        coro()
        await asyncio.sleep(wait)


async def execute_and_wait_seq(seq, coro):
    for s in seq:
        await execute_and_wait(coro, s)


async def my_app():
    def door_state(status):
        log.info("door_State\t\tPublishing state %s to DOOR_STATE_TOPIC", status)
        publish = client.publish(DOOR_STATE_TOPIC, status, 1)
        loop.create_task(publish)

    def door_target(status):
        log.info("door_target\t\tDoing nothing - empty function")
        # publish = client.publish(DOOR_TARGET_TOPIC, status, 1)
        # loop.create_task(publish)

    ds = DoorSensor(door_state_cb=door_state, door_target_cb=door_target)

    def new_door_status(movement, position):
        log.info("new_door_status\t\tNew door status received from mock motor, switches being updated accordingly")
        if position == Position.CLOSED:
            ds.closed_sensor_pin.on()
        elif position == Position.OPEN:
            ds.open_sensor_pin.on()

        if movement == Movement.OPENING:
            ds.closed_sensor_pin.off()
        elif movement == Movement.CLOSING:
            ds.open_sensor_pin.off()

    mm = MockMotor(door_status_cb=new_door_status, loop=loop, log_detailed_progress=True)




    def stop_and_return():
        if ds.movement in [Movement.OPENING, Movement.CLOSING]: # Somehting missing here, we shoudl also be checking direction again in case it reached it?
            log.info("stop_and_return\t\tStopping a %s door", Movement.description[ds.movement])
            mm.toggle()
            ds.door_stopped_while_moving()
            time.sleep(1) # TO-DO: Investigate effects of this synchronous sleep and potential bugs
            log.info("stop_and_return\t\tNow %s the door", Movement.description[ds.next_movement])
            mm.toggle()
            ds.door_started_while_stopped()

    debouncer = Delay_ms(stop_and_return, duration=1000)

    def subs_cb(topic, msg_str, retained):

        msg_str = msg_str.decode('utf-8')
        topic_str = topic.decode('utf-8')
        log.info("subs_cb\t\t\tReceived topic %s with payload %s", topic_str, msg_str)
        if topic == DOOR_TARGET_TOPIC.encode('utf-8') and retained is False:
            set_target(msg_str)

    def set_target(target):
        # Reversing the direction
        if ds.movement in [Movement.OPENING, Movement.CLOSING]:
            if Position.description[ds.next_movement] != target:
                debouncer.trigger()
                return
            else:
                debouncer.stop()

        if Position.description[mm.position] == target:
            log.info("set_target\t\tIgnoring request, already at target state")

        elif target == Position.description[ds.movement]:
            log.info("set_target\t\tIgnoring request, already heading in that direction")
        else:
            # Resuming movement from a stopped start
            if ds.movement == Movement.STOPPED and Position.description[ds.next_movement] == target:
                log.info("set_target\t\tStarting %s from a %s state",
                         Movement.description[ds.next_movement], Movement.description[Movement.STOPPED])
                mm.toggle()

    async def conn_han(cclient):
        await cclient.subscribe(DOOR_TARGET_TOPIC, 1)

    # MQTTClient.DEBUG = True  # Optional: print diagnostic messages
    config['subs_cb'] = subs_cb
    config['connect_coro'] = conn_han
    client = MQTTClient(config)


    # mm = MockMotor(door_sensor=ds, door_position_cb=yoyoyo, loop=loop, log_detailed_progress=True, current_time_to_open=5000, next_move_direction=Movement.CLOSING, movement=Movement.STOPPED)

    await client.connect()
    await asyncio.sleep(1)
    # Update DoorSensor pins based on MockMotor initialisation state
    new_door_status(mm.movement, mm.position)
    publish = client.publish(DOOR_TARGET_TOPIC, Position.description[mm.position], 1)
    loop.create_task(publish)
    await asyncio.sleep(1)
    # mm.start()
    # mm = MockMotor(door_position_cb=yoyoyo, loop=loop, log_detailed_progress=True)

    # loop.create_task(execute_and_wait_seq([], mm.toggle))
    # loop.create_task(execute_and_wait_seq([None], mm.toggle))
    # loop.create_task(execute_and_wait_seq([13, 13, 13], mm.toggle))
    loop.run_forever()
    loop.close()
    asyncio.new_event_loop()

asyncio.run(my_app())  # Run main application code)