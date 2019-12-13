from umqtt.simple import MQTTClient
from switch import Switch
import machine
import ubinascii
import time

from config import SERVER, COMMAND_TOPIC, STATE_TOPIC, TARGET_TOPIC, AVAILABILITY_TOPIC, RELAY_PIN, OPEN_SENSOR_PIN, CLOSED_SENSOR_PIN, PUSH_BUTTON_PIN

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

relay_pin = None


def new_msg(topic, msg):
    print("Received {} on {} topic".format(msg, topic))
    print("Turning relay on")
    relay_pin.value(1)
    time.sleep_ms(600)
    print("Turning relay off")
    relay_pin.value(0)


def main():
    global relay_pin

    client = MQTTClient(CLIENT_ID, SERVER)
    client.set_callback(new_msg)

    try:
        client.connect()
    except OSError:
        print("MQTT Broker seems down")
        print("Resetting after 20 seconds")
        time.sleep(20)
        machine.reset()

    client.subscribe(COMMAND_TOPIC)

    # Publish as available once connected
    client.publish(AVAILABILITY_TOPIC, "online", retain=True)
    # TO-DO: add concept of Open and closed sensor pins and use their changing state and timing to determine open/closing,
    # as well as using timing and Open/Close commands received while opening to determine Stopped state
    # Ensure manual triggers of opening via push button are configured.
    open_switch_pin = machine.Pin(OPEN_SENSOR_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    open_reed_switch = Switch(open_switch_pin)
    closed_switch_pin = machine.Pin(CLOSED_SENSOR_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    closed_reed_switch = Switch(closed_switch_pin)

    # Initialize state of garage door after booting up
    if open_switch_pin.value():
        client.publish(STATE_TOPIC, "Open", retain=True)
    elif closed_switch_pin.value():
        client.publish(STATE_TOPIC, "Closed", retain=True)
    else:
        client.publish(STATE_TOPIC, "Stopped", retain=True) # Assumes the door isn't in the process of opening or closing on power-up

    relay_pin = machine.Pin(RELAY_PIN, machine.Pin.OUT, 0)

    try:
        while True:

            open_reed_switch_new_value = False
            closed_reed_switch_new_value = False

            # Disable interrupts for a short time to read shared variable
            irq_state = machine.disable_irq()
            if open_reed_switch.new_value_available:
                open_reed_switch_value = open_reed_switch.value
                open_reed_switch_new_value = True
                open_reed_switch.new_value_available = False
            if closed_reed_switch.new_value_available:
                closed_reed_switch_value = closed_reed_switch.value
                closed_reed_switch_new_value = True
                closed_reed_switch.new_value_available = False
            machine.enable_irq(irq_state)

            # If the reed switches have a new value, publish the new state
            if open_reed_switch_new_value:
                if open_reed_switch_value:
                    print("Publishing Closing message")
                    client.publish(TARGET_TOPIC, "Closed")
                    client.publish(STATE_TOPIC, "Closing")
                else:
                    print("Publishing Open message")
                    client.publish(STATE_TOPIC, "Open")
            if closed_reed_switch_new_value:
                if closed_reed_switch_value:
                    print("Publishing Opening message")
                    client.publish(TARGET_TOPIC, "Open")
                    client.publish(STATE_TOPIC, "Opening")
                else:
                    print("Publishing Closed message")
                    client.publish(STATE_TOPIC, "Closed")

            # TO-DO: Add derived 'Opening' and  'Closing' states to logic
                # else:
                #     client.publish(STATE_TOPIC, "closed")

            # Process any MQTT messages
            if client.check_msg():
                client.wait_msg()

            time.sleep(1)

    finally:
        client.publish(AVAILABILITY_TOPIC, "offline", retain=False)
        client.disconnect()
        machine.reset()


main()

# Should never leave main() function, but if program crashes reset
machine.reset()
