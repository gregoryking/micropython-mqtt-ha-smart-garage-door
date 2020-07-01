
import machine


from machine import Pin
import uasyncio as asyncio
from aswitch import Switch

from config import OPEN_SENSOR_PIN

# from config import SERVER, COMMAND_TOPIC, STATE_TOPIC, TARGET_TOPIC, AVAILABILITY_TOPIC
# CLIENT_ID = ubinascii.hexlify(machine.unique_id())

# def main():
#     print("Running main")
#     client = MQTTClient(CLIENT_ID, SERVER)
#
#     try:
#         client.connect()
#     except OSError:
#         print("MQTT Broker seems down")
#         print("Resetting after 20 seconds")
#         time.sleep(20)
#         machine.reset()
#
#     def process_mqtt_msg(topic, msg):
#         # TO-DO: Check mqttthing is definitely sending closed/open status requests.
#         print("Received {} on {} topic".format(msg, topic))
#         if msg == b"Open":
#             door_controller.open()
#         elif msg == b"Closed":
#             door_controller.close()
#         # To simulate push button presses in absence of spare input pins for testing
#         elif msg == b"PRESSED":
#             door_controller.push_button(True)
#         elif msg == b"RELEASED":
#             door_controller.push_button(False)
#
#
#     # Publish as available once connected
#     client.publish(AVAILABILITY_TOPIC, "online", retain=True)
#     # TO-DO: add concept of Open and closed sensor pins and use their changing state and timing to determine open/closing,
#     # as well as using timing and Open/Close commands received while opening to determine Stopped state
#     # Ensure manual triggers of opening via push button are configured.
#     print("Initialising DoorState and DoorController...")
#
#     # Initiatlise DoorState and DoorController
#     door_state = DoorState(client)
#     door_controller = DoorController(door_state)
#
#     client.set_callback(process_mqtt_msg)
#     client.subscribe(COMMAND_TOPIC)
#
#     try:
#         while True:
#             # Update DoorState and DoorController
#             door_state.update()
#             door_controller.update()
#
#             # Process any MQTT messages
#             if client.check_msg():
#                 client.wait_msg()
#
#             time.sleep(1)
#
#     finally:
#         client.publish(AVAILABILITY_TOPIC, "offline", retain=False)
#         client.disconnect()
#         machine.reset()


def toggle():
    print("Toggled")

async def my_app():
    await asyncio.sleep(600)  # Dummy

Switch.debounce_ms=50

pin = Pin(OPEN_SENSOR_PIN, Pin.IN, Pin.PULL_UP)  # Pushbutton to gnd
sw = Switch(pin)
sw.close_func(toggle, ())  # Note how coro and args are passed
loop = asyncio.get_event_loop()
loop.run_until_complete(my_app())  # Run main application code

# main()



# Should never leave main() function, but if program crashes reset
machine.reset()
