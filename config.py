ESSID = ***REMOVED***
PASSWORD = ***REMOVED***
SERVER = "192.168.1.128"

COMMAND_TOPIC = "home/garage/garagedoor/set"
STATE_TOPIC = "home/garage/garagedoor"
TARGET_TOPIC = "home/garage/garagedoortarget"
AVAILABILITY_TOPIC = "home/garage/garagedoor/available"


# Hardware Pin scheme
# corrected?
#         Y                             Y     ?                      Y
# [ + ] [12 ] [ - ] [ 5 ] [ x ] [ x ] [ 4 ] [ 0 ] [  ] [ + ] [ 3 ] [ 1 ] 
#                                                         VDD   RX   TX

RELAY_PIN=12
OPEN_SENSOR_PIN=4
CLOSED_SENSOR_PIN=1
PUSH_BUTTON_PIN=5