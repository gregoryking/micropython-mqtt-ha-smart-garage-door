from .mqtt_as import MQTTClient, config
from config import DOOR_TARGET_TOPIC, DOOR_PUSH_BUTTON_TOPIC, MQTT_SERVER
import logging

log = logging.getLogger("MQTT")

class MQTT:

    def __init__(self, subscription_cb=None):
        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        config['server'] = MQTT_SERVER
        if subscription_cb is not None:
            config['subs_cb'] = subscription_cb
        else:
            config['subs_cb'] = MQTT.default_subscription_cb
        config['connect_coro'] = MQTT.connection_handler
        self.__client = MQTTClient(config)

    async def connect(self):
        return await self.__client.connect()

    def publish(self, topic, msg, qos=1):
        return self.__client.publish(topic, msg)

    def default_subscription_cb(topic, msg_str, retained):
        msg_str = msg_str.decode('utf-8')
        topic_str = topic.decode('utf-8')
        log.info("subs_cb\t\t\tReceived topic %s with payload %s", topic_str, msg_str)

    async def connection_handler(cclient):
        await cclient.subscribe(DOOR_TARGET_TOPIC, 1)
        await cclient.subscribe(DOOR_PUSH_BUTTON_TOPIC, 1)