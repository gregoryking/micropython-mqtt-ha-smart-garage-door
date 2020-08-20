import unittest
from kooji.motor.mockmotor import MockMotor
from kooji.enums import Movement, Position
import uasyncio as asyncio

# print("file is:{}".format(__file__))
# print("name is:{}".format(__name__))

unit_test_transition_duration = 100
unit_test_refresh_ms = 10


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


def setup_and_run(seq):

    def door_status_cb(dummy1, dummy2):
        pass

    mm = MockMotor(door_status_cb=door_status_cb, loop=loop, log_detailed_progress=True)

    coro = mm.toggle
    # loop.run_until_complete(simple_open_stop_close(loop))
    loop.run_until_complete(execute_and_wait_seq(seq, coro))
    loop.close()
    asyncio.new_event_loop()
    return mm.position


# TO-DO, make the 2000 times relative to test configuration parameters
class DoorActuatorRunRequests(unittest.TestCase):
    """Tests for stubbing."""

    def test_double_click(self):
        position = setup_and_run([0, None])
        self.assertTrue(position == Position.OPEN)

    def test_triple_click(self):
        position = setup_and_run([0, 0, None])
        self.assertTrue(position == Position.OPEN)

    def test_triple_click_double_click_stop_close(self):
        position = setup_and_run([0, 0, 2, 0, 2, None])
        self.assertTrue(position == Position.CLOSED)

    def test_go_nuts(self):
        position = setup_and_run([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None])
        self.assertTrue(position == Position.OPEN)

    def test_double_click_pause_click(self):
        position = setup_and_run([0, 2, None])
        self.assertTrue(position == Position.PART_OPEN)

    def test_double_click_stop(self):
        position = setup_and_run([0, 2, None])
        self.assertTrue(position == Position.PART_OPEN)

    def test_open_stop_close(self):
        position = setup_and_run([2, 2, None])
        self.assertTrue(position == Position.CLOSED)

    def test_open(self):
        position = setup_and_run([None])
        self.assertTrue(position == Position.OPEN)

    def test_open_then_close(self):
        position = setup_and_run([None, None])
        self.assertTrue(position == Position.CLOSED)

    def test_open_then_close_then_open_then_close(self):
        position = setup_and_run([None, None, None, None])
        self.assertTrue(position == Position.CLOSED)

    def test_open_then_close_then_open(self):
        position = setup_and_run([None, None, None])
        self.assertTrue(position == Position.OPEN)

    def test_open_stop_close_stop_open(self):
        position = setup_and_run([4, 2, 2, 3, None])
        self.assertTrue(position == Position.OPEN)


if __name__ == '__main__':
    unittest.main()