ESSID = ***REMOVED***
PASSWORD = ***REMOVED***
SERVER = "192.168.1.128"

COMMAND_TOPIC = "home/garage/garagedoor/set"
STATE_TOPIC = "home/garage/garagedoor"
TARGET_TOPIC = "home/garage/garagedoortarget"
AVAILABILITY_TOPIC = "home/garage/garagedoor/available"


# Hardware Pin scheme
#       v+12V                       vRX
# [12] [x] [x]            [4][0][X][1][3]
#           ^GND                 ^VDD  ^TX
RELAY_PIN=12
OPEN_SENSOR_PIN=4
CLOSED_SENSOR_PIN=1
PUSH_BUTTON_PIN=3
