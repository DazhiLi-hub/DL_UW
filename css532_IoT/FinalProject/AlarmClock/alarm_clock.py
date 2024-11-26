import threading
import time
from datetime import datetime

stop_event = threading.Event()

def alarm(wake_up_time):
    stop_event.clear()
    while True:
        current_time = datetime.strftime("%Y-%m-%d %H:%M:%S")
        print("Current time:", current_time)

        # Check if the current time matches the alarm time
        if current_time == wake_up_time:
            print("Time to wake up!")
            #TODO: buzzer sound and wait the button to be pressed
            break  # Exit the loop once the alarm goes off

        time.sleep(1)  # Check the time every 1 seconds