import time
from datetime import datetime
from gpiozero import Button
from gpiozero import Buzzer

def alarm(wake_up_time, stop_event):
    print("[INFO] Alarm starts")
    # stop alarming button at GPIO3
    button = Button(3)
    # buzzer at GPIO17
    buzzer = Buzzer(17)
    while not stop_event.is_set():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if the current time matches the alarm time
        if current_time == wake_up_time:
            print("[INFO] Time to wake up!")
            #buzzer sound and wait the button to be pressed
            buzzer.beep()
            while True:
                if button.is_pressed:
                    buzzer.off()
                    print("[INFO] Alarm stopped")
                    stop_event.set()
                    break
        time.sleep(1)  # Check the time every 1 seconds