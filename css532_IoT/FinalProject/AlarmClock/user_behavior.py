import threading
from datetime import datetime

from gpiozero import Button

from db_wrapper import db_wrapper

stop_event = threading.Event()

def listen_on_bed_time(sleep_at_time):
    stop_event.clear()
    button = Button(2)
    while not stop_event.is_set():
        button.wait_for_press()
        # if button pressed but the schedule is canceled, just return
        if stop_event.is_set():
            return
        # recording user data to database
        db = db_wrapper()
        db_result = db.insert_one_behavior(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sleep_at_time)
        # if user behavior collecting failed, no need to stop the program
        # here it should be log files, but for simplicity, just use print
        if (db_result.get('ResponseMetadata').get('HTTPStatusCode') != 200):
            print("[ERROR] Inserting user behavior failed, please check. ")
            print("[ERROR] db response: " + db_result)
        else:
            print("[INFO] User behavior uploaded database successfully")
        stop_event.set()

    return