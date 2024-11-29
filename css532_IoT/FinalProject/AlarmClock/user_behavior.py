import time
from datetime import datetime, timedelta

from gpiozero import Button

import msg_sender
from db_wrapper import db_wrapper

def listen_on_bed_time(sleep_at_time, to_phone_number, stop_event):
    print("[INFO] user behavior collecting starts")
    # assign button
    button = Button(2)
    # notification config
    msg_time_interval = 10
    max_notify_times = 5
    notify_times_count = 0
    while not stop_event.is_set():
        # check if uses is not in bed after sleep_at_time, send notification every x interval minutes
        target_time = datetime.strftime(datetime.now() - timedelta(minutes=msg_time_interval),
                                        "%Y-%m-%d %H:%M:%S")
        if target_time == sleep_at_time and notify_times_count < max_notify_times:
            msg_sender.send_sms(to_phone_number, str(msg_time_interval) + " past preset sleep time, hurry up")
            msg_time_interval+=msg_time_interval
            notify_times_count += 1

        time.sleep(1)

        # when pressing button, record the user's real sleep at time
        if button.is_pressed:
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