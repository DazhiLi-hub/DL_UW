import mqtt_wrapper

is_alarming_mode = False

if __name__ == '__main__':
    while True:
        mqtt = mqtt_wrapper.mqtt_wrapper()
        # if no alarms is set yet, listen on time schedule topics for receiving new time schedule
        if not is_alarming_mode:
            mqtt.receive_time_schedule_msg()
            is_alarming_mode = True
        # if alarm was set, then listen on schedule cancel topics for canceling previous time schedule
        else:
            mqtt.receive_cancel_schedule_msg()
            is_alarming_mode = False
