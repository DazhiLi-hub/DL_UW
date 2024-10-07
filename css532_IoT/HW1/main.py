from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import json

ENDPOINT = 'a10y5hwkjz8v5p-ats.iot.us-east-1.amazonaws.com'
CERT_FILE = './Mac.cert.pem'
PRIVATE_KEY = './Mac.private.key'
CA_FILE = 'root-CA.crt'
CLIENT_ID = "Dazhi's Macbook"
SEND_MESSAGE_TOPIC = 'HW1/MsgFromThings'
RCV_MESSAGE_TOPIC = 'HW1/MsgFromRepublish'
received_all_event = threading.Event()
received_data = None

message_string = '{"temperatures" : [77,88,99,70,90,67,85,73,89]}'
is_send_feedback = False

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_data
    received_data = json.loads(payload)
    if received_data['temperature']:
        global is_send_feedback
        is_send_feedback = True
    received_all_event.set()

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")

if __name__ == '__main__':
    # Create a MQTT connection from the global variables
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT_FILE,
        pri_key_filepath=PRIVATE_KEY,
        ca_filepath=CA_FILE,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)

    print(f"Connecting to aws west-2 IoT Core with client ID {CLIENT_ID}")

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(RCV_MESSAGE_TOPIC))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=RCV_MESSAGE_TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    received_all_event.wait()

    # If receive the message, which is requesting temperature data, then publish temperature data
    if is_send_feedback:
        print("Publishing message to topic '{}': {}".format(SEND_MESSAGE_TOPIC, message_string))
        message_json = json.dumps(message_string)
        mqtt_connection.publish(
            topic=SEND_MESSAGE_TOPIC,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
