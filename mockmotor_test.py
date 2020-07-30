import uasyncio as asyncio
from kooji.motor.mockmotor import MockMotor
from kooji.doorsensor import DoorSensor
from kooji.enums import Movement, Position


def yoyoyo(movement, position):
    pass
    # print("**************** Movement: {movement} | Position: {position}".format(movement=Movement.description[movement], position=Position.description[position]))

def print_remaining(d):
    print("Hello {remaining}".format(remaining=d.time_remaining))


loop = asyncio.get_event_loop()
ds = DoorSensor()
# mm = MockMotor(door_sensor=ds, door_position_cb=yoyoyo, loop=loop, log_detailed_progress=True, current_time_to_open=5000, next_move_direction=Movement.CLOSING, movement=Movement.STOPPED)
mm = MockMotor(door_sensor=ds, door_position_cb=yoyoyo, loop=loop, log_detailed_progress=True)
# mm = MockMotor(door_position_cb=yoyoyo, loop=loop, log_detailed_progress=True)


async def execute_and_wait(coro, wait):
    if wait is None:
        await coro()
    elif wait == 0:
        coro()
    else:
        coro()
        await asyncio.sleep(wait)


async def run_tasks():
    await execute_and_wait(mm.toggle, 3)
    await execute_and_wait(mm.toggle, None)
    await execute_and_wait(mm.toggle, None)

async def execute_and_wait_seq(seq):
    for s in seq:
        await execute_and_wait(mm.toggle, s)


async def my_app():
    # loop.create_task(run_tasks())
    loop.create_task(execute_and_wait_seq([3, None, None]))
    loop.run_forever()
    # loop.run_until_complete(run_tasks())
    loop.close()
    asyncio.new_event_loop()

asyncio.run(my_app())  # Run main application code)