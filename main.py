from kooji.motor.dooractuator import DoorActuator
import uasyncio as asyncio

async def main():
    my_motor = DoorActuator(lambda x: print('State is ' + str(x)))
    my_motor.run()
    await asyncio.sleep(1000)


asyncio.run(main())
#
# # Should never leave main() function, but if program crashes reset
# machine.reset()
