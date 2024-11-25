from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
import sys

ENDPOINT = 'a10y5hwkjz8v5p-ats.iot.us-east-1.amazonaws.com'
CERT_FILE = './client_server.cert.pem'
PRIVATE_KEY = './client_server.private.key'
CA_FILE = './root-CA.crt'
CLIENT_ID = "Client Server"
SEND_MESSAGE_TOPIC = 'system/time_schedule'

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

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(
        callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")

class mqtt_wrapper:
    def __init__(self):
        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
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

    def publish_msg(self, message_json):
        connect_future = self.mqtt_connection.connect()
        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")

        self.mqtt_connection.publish(
            topic=SEND_MESSAGE_TOPIC,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)

        # Disconnect
        print("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")