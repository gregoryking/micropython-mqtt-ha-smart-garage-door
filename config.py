# Wireless Credentials
ESSID = ***REMOVED***
PASSWORD = ***REMOVED***

# MQTT
# SERVER = "mqttserver"
SERVER = "192.168.1.137"
COMMAND_TOPIC = "home/garage/garagedoor/set"
STATE_TOPIC = "home/garage/garagedoor"
TARGET_TOPIC = "home/garage/garagedoortarget"
AVAILABILITY_TOPIC = "home/garage/garagedoor/available"

# Full time taken for door to move from open to closed or vice versa (ms)
TRANSITION_DURATION = 15000

# Hardware Pin scheme
# +12v  GPIO  GND   GPIO              GPIO  GPIO  +3.3v +3.3v GPIO  GPIO
# [ + ] [12 ] [ - ] [ 5 ] [ x ] [ x ] [ 4 ] [ 0 ] [ + ] [ + ] [ 3 ] [ 1 ] 
#                                                         VDD   RX   TX

RELAY_PIN=12 # Need to test this works as a relap pin (12 worked previously 12?)
OPEN_SENSOR_PIN=4
# CLOSED_SENSOR_PIN=3  # Would ideally free up this sensor pin to allow serial debugging and updates
CLOSED_SENSOR_PIN=5 #Use 3 here once debugging complete, 0 for interim tresting. set to unusable 5 while using 0 for other testing?
PUSH_BUTTON_PIN=0 # 5 doesn't work as pushbutton?

# DoorController ConfigurationPulse
# MOVE_PULSE_DURATION = 600
# STOP_PULSE_DURATION = 300
# WAIT_DURATION = 1000
MOVE_PULSE_DURATION = 6000
STOP_PULSE_DURATION = 3000
WAIT_DURATION = 10000

CLOSE_WITH_DELAY_PUSH_BUTTON_TRIGGER_TIME =3000
CLOSE_WITH_DELAY_CLOSE_DELAY = 10000

HIGH, LOW = 1, 0

START_COMMANDS = [
    {
        "pinLevel": HIGH,
        "duration": MOVE_PULSE_DURATION
    },        
    {
        "pinLevel": LOW,
        "duration": WAIT_DURATION
    }
]

STOP_COMMANDS = [
    {
        "pinLevel": HIGH,
        "duration": STOP_PULSE_DURATION
    },
    {
        "pinLevel": LOW,
        "duration": WAIT_DURATION
    }
]

STOP_AND_RETURN_COMMANDS = STOP_COMMANDS + START_COMMANDS
