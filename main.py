import uasyncio as asyncio
from kooji.doorsensor import DoorSensor
from kooji.dooractuator import DoorActuator

async def main():

    da = await DoorActuator.create()

    while True:
        await asyncio.sleep(60)


asyncio.run(main())

# # Should never leave main() function, but if program crashes reset
# machine.reset()
