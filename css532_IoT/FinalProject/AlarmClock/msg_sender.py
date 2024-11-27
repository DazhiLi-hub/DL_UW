import threading

stop_event = threading.Event()

def send_message(msg_notify_time):
    stop_event.clear()
    while not stop_event.is_set():
        print("Unimplemented")
        #TODO: send message when notify_at_time
        stop_event.set()