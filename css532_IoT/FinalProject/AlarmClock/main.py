import threading
import time

import mqtt_wrapper

TIME_SCHEDULE_EVENT = threading.Event()
CANCEL_SCHEDULE_EVENT = threading.Event()


if __name__ == '__main__':
    mqtt = mqtt_wrapper.mqtt_wrapper()
    # listen on time schedule topics for receiving new time schedule
    schedule_thread = threading.Thread(target=mqtt.receive_time_schedule_msg, args=([TIME_SCHEDULE_EVENT]))
    schedule_thread.start()
    # listen on schedule cancel topics for canceling previous time schedule
    cancel_thread = threading.Thread(target=mqtt.receive_cancel_schedule_msg, args=([TIME_SCHEDULE_EVENT]))
    cancel_thread.start()
    time.sleep(1)
    user_input = input("Enter 'q' to quit the whole program: ")
    if user_input.lower() == 'q':
        TIME_SCHEDULE_EVENT.set()
        CANCEL_SCHEDULE_EVENT.set()
        mqtt_wrapper.clean_all_threads()
        schedule_thread.join()
        cancel_thread.join()
        mqtt.disconnect()