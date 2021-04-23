import paho.mqtt.client as mqtt #import the client1
from smartbell import SmartBell
class MyMQTT:
    __instance__  : mqtt.Client = None

    def __init__(self, host: str, port: int ):
        if not MyMQTT.__instance__ :
            MyMQTT.__instance__ = mqtt.Client()
            MyMQTT.__instance__.connect(host, port)

    @staticmethod
    def send(topic, message, host="localhost", port=1883):
        my_mqtt = MyMQTT(host, port)
        msg = SmartBell.get_names_list(message)
        # send mqtt message
        MyMQTT.__instance__.publish(topic,msg)
        return