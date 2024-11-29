import threading
import json

from awscrt import mqtt
from awsiot import mqtt_connection_builder
import sys

import alarm_clock
import msg_sender
import user_behavior

ENDPOINT = 'a10y5hwkjz8v5p-ats.iot.us-east-1.amazonaws.com'
CERT_FILE = './alarm_clock.cert.pem'
PRIVATE_KEY = './alarm_clock.private.key'
CA_FILE = './root-CA.crt'
CLIENT_ID = "Alarm Clock"
RECV_TIME_SCHEDULE_TOPIC = 'system/time_schedule'
RECV_CANCEL_SCHEDULE_TOPIC = 'system/cancel_schedule'

MSG_THREADS = {}
USER_THREADS = {}
ALARM_THREADS = {}

def cancel_schedule_by_id(id):
    if id in MSG_THREADS:
        msg_thread, msg_stop_event = MSG_THREADS[id]
        usr_thread, usr_stop_event = USER_THREADS[id]
        alarm_thread, alarm_stop_event = ALARM_THREADS[id]
        if not msg_stop_event.is_set():
            msg_stop_event.set()
            msg_thread.join()
            print(f"[INFO] Message notification thread {id} has been canceled.")
        if not usr_stop_event.is_set():
            usr_stop_event.set()
            usr_thread.join()
            print(f"[INFO] User behaviors collecting thread {id} has been canceled.")
        if not alarm_stop_event.is_set():
            alarm_stop_event.set()
            alarm_thread.join()
            print(f"[INFO] Alarming thread {id} has been canceled.")
    else:
        print(f"[WARN] Thread {id} not found.")

def clean_all_threads():
    for thread, stop_event in MSG_THREADS.items():
        if not stop_event.is_set():
            stop_event.set()
            thread.join()
    for thread, stop_event in USER_THREADS.items():
        if not stop_event.is_set():
            stop_event.set()
            thread.join()
    for thread, stop_event in ALARM_THREADS.items():
        if not stop_event.is_set():
            stop_event.set()
            thread.join()

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

# Callback when the subscribed topic receives a message
def on_time_schedule_received(topic, payload, dup, qos, retain, **kwargs):
    #parsing payload; eg. "2024-11-27 08:20:00" (time format, type = str)
    time_schedule = json.loads(payload.decode('utf-8'))
    wake_up_time = time_schedule.get('wake_up_time')
    sleep_at_time = time_schedule.get('sleep_at_time')
    msg_notify_time = time_schedule.get('msg_notify_time')
    to_phone_number = time_schedule.get('to_phone_number')
    id = time_schedule.get('id')
    print('[INFO] id=' + id + ' schedule received')


    # sending sleep message thread
    msg_thread_stop_event = threading.Event()
    msg_thread = threading.Thread(target=msg_sender.send_message, kwargs={'msg_notify_time': msg_notify_time,
                                                                          'sleep_at_time': sleep_at_time,
                                                                          'to_phone_number': to_phone_number,
                                                                          'stop_event': msg_thread_stop_event})
    MSG_THREADS[id] = (msg_thread, msg_thread_stop_event)

    # recording user's behavior thread
    usr_thread_stop_event = threading.Event()
    usr_thread = threading.Thread(target=user_behavior.listen_on_bed_time, kwargs={'sleep_at_time': sleep_at_time,
                                                                                   'to_phone_number': to_phone_number,
                                                                                   'stop_event': usr_thread_stop_event})
    USER_THREADS[id] = (usr_thread, usr_thread_stop_event)

    # alarming wakeup thread
    alarm_thread_stop_event = threading.Event()
    alarm_thread = threading.Thread(target=alarm_clock.alarm, kwargs={'wake_up_time': wake_up_time,
                                                                      'stop_event': alarm_thread_stop_event})
    ALARM_THREADS[id] = (alarm_thread, alarm_thread_stop_event)

    msg_thread.start()
    usr_thread.start()
    alarm_thread.start()

def on_schedule_cancel_received(topic, payload, dup, qos, retain, **kwargs):
    cancel_schedule = json.loads(payload.decode('utf-8'))
    id = cancel_schedule.get('id')
    cancel_schedule_by_id(id)

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

        connect_future = self.mqtt_connection.connect()
        # Future.result() waits until a result is available
        connect_future.result()
        print("\n[INFO] MQTT Connected successfully!")

    def receive_time_schedule_msg(self, stop_event):
        # Subscribe
        print("[INFO] Subscribing to topic '{}'...".format(RECV_TIME_SCHEDULE_TOPIC))
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=RECV_TIME_SCHEDULE_TOPIC,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_time_schedule_received)

        subscribe_result = subscribe_future.result()
        print("[INFO] Subscribed with {}".format(str(subscribe_result['qos'])))

        stop_event.wait()

    def receive_cancel_schedule_msg(self, stop_event):
        # Subscribe
        print("[INFO] Subscribing to topic '{}'...".format(RECV_CANCEL_SCHEDULE_TOPIC))
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=RECV_CANCEL_SCHEDULE_TOPIC,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_schedule_cancel_received)

        subscribe_result = subscribe_future.result()
        print("[INFO] Subscribed with {}".format(str(subscribe_result['qos'])))

        stop_event.wait()

    def disconnect(self):
        # Disconnect
        print("[INFO] Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("[INFO] Disconnected!")