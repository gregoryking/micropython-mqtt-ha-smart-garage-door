import unittest
from kooji.dooractuator import DoorActuator
import uasyncio as asyncio

# print("file is:{}".format(__file__))
# print("name is:{}".format(__name__))

unit_test_transition_duration = 100
unit_test_refresh_ms = 10


async def run_and_wait(loop, coro, wait=None):
    task = loop.create_task(coro)
    if wait is None:
        await task
    else:
        await asyncio.sleep_ms(wait)


async def run_and_wait_seq(loop, coro, seq):
    for i in seq:
        # Adjust timings for sped up unittests
        delay = i
        if i is not None:
            delay = int(delay * (unit_test_transition_duration / DoorActuator.default_transition_time_total))
        # print("test is goign to wait ", str(delay))
        await run_and_wait(loop, coro(), delay)


def setup_and_run(seq):
    # actuator = DoorActuator()
    actuator = DoorActuator(transition_duration=unit_test_transition_duration, refresh_ms=unit_test_refresh_ms)
    loop = asyncio.get_event_loop()
    coro = actuator.run
    # loop.run_until_complete(simple_open_stop_close(loop))
    loop.run_until_complete(run_and_wait_seq(loop, coro, seq))
    loop.close()
    asyncio.new_event_loop()
    return  actuator.position


# TO-DO, make the 2000 times relative to test configuration parameters
class DoorActuatorRunRequests(unittest.TestCase):
    """Tests for stubbing."""

    def test_double_click(self):
        position = setup_and_run([0, None])
        self.assertTrue(position == DoorActuator.OPEN)

    def test_triple_click(self):
        position = setup_and_run([0, 0, None])
        self.assertTrue(position == DoorActuator.OPEN)

    def test_triple_click_double_click_stop_close(self):
        position = setup_and_run([0, 0, 2000,0,2000, None])
        self.assertTrue(position == DoorActuator.CLOSED)

    def test_go_nuts(self):
        position = setup_and_run([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None])
        self.assertTrue(position == DoorActuator.OPEN)

    def test_double_click_pause_click(self):
        position = setup_and_run([0, 2000, None])
        self.assertTrue(position == DoorActuator.PART_OPEN)

    def test_double_click_stop(self):
        position = setup_and_run([0, 2000, None])
        self.assertTrue(position == DoorActuator.PART_OPEN)

    def test_open_stop_close(self):
        position = setup_and_run([2000, 2000, None])
        self.assertTrue(position == DoorActuator.CLOSED)

    def test_open(self):
        position = setup_and_run([None])
        self.assertTrue(position == DoorActuator.OPEN)

    def test_open_then_close(self):
        position = setup_and_run([None, None])
        self.assertTrue(position == DoorActuator.CLOSED)

    def test_open_then_close_then_open_then_close(self):
        position = setup_and_run([None, None, None, None])
        self.assertTrue(position == DoorActuator.CLOSED)

    def test_open_then_close_then_open(self):
        position = setup_and_run([None, None, None])
        self.assertTrue(position == DoorActuator.OPEN)

    def test_open_stop_close_stop_open(self):
        position = setup_and_run([4000, 2000, 2000, 3000, None])
        self.assertTrue(position == DoorActuator.OPEN)


if __name__ == '__main__':
    unittest.main()