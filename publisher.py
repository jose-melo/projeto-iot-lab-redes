import time

from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 8080
topic = "test/zezin"
# generate client ID with pub prefix randomly
client_id = 'publisher'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
       print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def configure():
    client = connect_mqtt()
    client.loop_start()
    return client

def run():
	client = configure()
	publish(client, "teste")


if __name__ == '__main__':
    run()