import threading

stop_event = threading.Event()
def listen_on_bed_time():
    stop_event.clear()
    return