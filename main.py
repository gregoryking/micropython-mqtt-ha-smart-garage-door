from umqtt.simple import MQTTClient
from switch import Switch
from doorstate import DoorState
import machine
import ubinascii
import time

from config import SERVER, COMMAND_TOPIC, STATE_TOPIC, TARGET_TOPIC, AVAILABILITY_TOPIC, RELAY_PIN, OPEN_SENSOR_PIN, CLOSED_SENSOR_PIN, PUSH_BUTTON_PIN

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

relay_pin = None


def toggleRelay():
    print("Turning relay on")
    relay_pin.value(1)
    time.sleep_ms(600)
    print("Turning relay off")
    relay_pin.value(0)

def new_msg(topic, msg):
    print("Received {} on {} topic".format(msg, topic))
    toggleRelay()

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
    push_button_pin = machine.Pin(PUSH_BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    push_button = Switch(push_button_pin)

    # Initialize state of garage door after booting up
    if not open_switch_pin.value():
        client.publish(STATE_TOPIC, "Open", retain=True)
    elif not closed_switch_pin.value():
        client.publish(STATE_TOPIC, "Closed", retain=True)
    else:
        client.publish(STATE_TOPIC, "Stopped", retain=True) # Assumes the door isn't in the process of opening or closing on power-up
    door_state = DoorState(open_reed_switch, closed_reed_switch, client)

    relay_pin = machine.Pin(RELAY_PIN, machine.Pin.OUT, 0)

    try:
        while True:

            open_reed_switch_new_value = False
            closed_reed_switch_new_value = False
            push_button_new_value = False

            # Disable interrupts for a short time to read shared variable
            irq_state = machine.disable_irq()
            if open_reed_switch.new_value_available:
                open_reed_switch_value = not open_reed_switch.value
                open_reed_switch_new_value = True
                open_reed_switch.new_value_available = False
            if closed_reed_switch.new_value_available:
                closed_reed_switch_value = not closed_reed_switch.value
                closed_reed_switch_new_value = True
                closed_reed_switch.new_value_available = False
            if push_button.new_value_available:
                push_button_value = not push_button.value
                push_button_new_value = True
                push_button.new_value_available = False
            machine.enable_irq(irq_state)

            # If the reed switches have a new value, publish the new state
            if open_reed_switch_new_value:
                if open_reed_switch_value:
                    door_state.end_door_transition()
                    print("Publishing Open message")
                    client.publish(STATE_TOPIC, "Open")
                else:
                    door_state.start_door_transition()
                    print("Publishing Closing message")
                    client.publish(TARGET_TOPIC, "Closed")
                    client.publish(STATE_TOPIC, "Closing")
            if closed_reed_switch_new_value:
                if closed_reed_switch_value:
                    door_state.end_door_transition()
                    print("Publishing Closed message")
                    client.publish(STATE_TOPIC, "Closed")
                else:
                    door_state.start_door_transition()
                    print("Publishing Opening message")
                    client.publish(TARGET_TOPIC, "Open")
                    client.publish(STATE_TOPIC, "Opening")
            if push_button_new_value:
                if push_button_value:
                    print("Push button depressed")
                else:
                    print("Push button RELEASED... triggering door action")
                    if door_state.moving:
                        client.publish(STATE_TOPIC, "Stopped")
                    toggleRelay()

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
