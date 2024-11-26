import threading

stop_event = threading.Event()

def send_message(sleep_at_time):
    stop_event.clear()
    return