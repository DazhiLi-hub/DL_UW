import os
import threading
import time
from datetime import datetime
from twilio.rest import Client

stop_event = threading.Event()

def send_message(msg_notify_time, sleep_at_time):
    stop_event.clear()
    print("[INFO] msg notification starts")
    while not stop_event.is_set():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if the current time matches the msg_notify_time
        if current_time == msg_notify_time:
            print("[INFO] Time to wake up!")
            send_sms("+12066881358", get_message_body(sleep_at_time))
            stop_event.set()
        time.sleep(1)  # Check the time every 1 seconds


def send_sms(to_phone_number, message):
    # Twilio credentials
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Send SMS
    result = client.messages.create(
        body=message,
        from_= os.environ['TWILIO_ORIGINATOR'],
        to=to_phone_number
    )
    if result.error_message:
        print("[ERROR] sending message failed:" + result.error_message)
    else:
        print(f"[INFO] Message sent! SID: {result.sid}")

def get_message_body(sleep_at_time):
    return ("Time to prepare for sleep, take a shower first\n" +
            "Please sleep at " + sleep_at_time + "\n" +
            "Wish you a good nigh\n" +
            "AlarmClockService")