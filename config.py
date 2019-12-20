# Wireless Credentials
ESSID = ***REMOVED***
PASSWORD = ***REMOVED***

# MQTT
SERVER = "192.168.1.128"
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

RELAY_PIN=12
OPEN_SENSOR_PIN=4
CLOSED_SENSOR_PIN=3  # Would ideally free up this sensor pin to allow serial debugging and updates
PUSH_BUTTON_PIN=0