from kooji.machine import Pin

# Wireless Credentials
ESSID =
PASSWORD =

# MQTT
# SERVER = "mqttserver"
MQTT_SERVER = "192.168.1.137"
DOOR_TARGET_TOPIC = "home/garage/garagedoor/target" # subscribe to and publish updates [Open, Closed]
DOOR_PUSH_BUTTON_TOPIC = "home/garage/garagedoor/pushbutton" # subscribe to and publish updates
DOOR_STATE_TOPIC = "home/garage/garagedoor/state" # publish updates [Open, Closed, Opening, Closing, Stopped]
AVAILABILITY_TOPIC = "home/garage/garagedoor/available"

# Full time taken for door to move from open to closed or vice versa (ms)
TRANSITION_TIME_MS = 10000


# Hardware Pin scheme
# +12v  GPIO  GND   GPIO                    GPIO  GPIO  +3.3v +3.3v GPIO  GPIO
# [ + ] [12 ] [ - ] [ 5 ] [ x ] [ x ] [ x ] [ 4 ] [ 0 ] [ + ] [ + ] [ 3 ] [ 1 ]
#                                                               VDD   RX   TX
# GPIO Number, pull, invert
RELAY_PIN = {"pinArgs": (5, Pin.OUT, Pin.PULL_UP), "inverted": False}
OPEN_SENSOR_PIN = {"pinArgs": (4, Pin.IN, Pin.PULL_UP), "inverted": False}
CLOSED_SENSOR_PIN = {"pinArgs": (14, Pin.IN, Pin.PULL_UP), "inverted": False}
PUSH_BUTTON_PIN = {"pinArgs": (12, Pin.IN, Pin.PULL_UP), "inverted": True}

MOVE_PULSE_DURATION = 1000
DEBOUNCE_MS = 500 + MOVE_PULSE_DURATION

CLOSE_WITH_DELAY_PUSH_BUTTON_TRIGGER_TIME =3000
CLOSE_WITH_DELAY_CLOSE_DELAY = 10000

HIGH, LOW = 1, 0