from time import sleep

import numpy as np
from datetime import datetime, timedelta

class time_schedule:
    """
    Time schedule builder based on user_behaviors, preset wakeup time, sleep period length
    """
    def __init__(self, user_behaviors, wake_up_time, prefer_sleep_time):
        # calculating wake up time
        now = datetime.now()
        target_time = now.replace(hour=int(wake_up_time.split(':')[0]),
                                  minute=int(wake_up_time.split(':')[1]),
                                  second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        self.wake_up_time = target_time

        # calculating sleep time
        prefer_sleep_time = prefer_sleep_time if prefer_sleep_time else 7
        self.sleep_at_time = target_time - timedelta(hours=prefer_sleep_time)

        # calculating message notification time
        time_shift = 3600
        if len(user_behaviors) > 0:
            time_shift += self.get_80_percentile_time(user_behaviors)

        self.msg_notify_time = self.sleep_at_time - timedelta(seconds=time_shift)

    def get_80_percentile_time(self, user_behaviors):
        time_shifts = []
        time_format = "%Y-%m-%d %H:%M:%S"
        for user_behavior in user_behaviors:
            #time_str = "2024-11-24 10:30:00"
            ideal_time = user_behavior.get('IDEAL_TIME')
            real_time = user_behavior.get('REAL_TIME')
            time_shift = datetime.strptime(real_time, time_format) - datetime.strptime(ideal_time, time_format)
            time_shifts.append(time_shift.total_seconds())
        time_shifts.sort()
        percentile_80 = np.percentile(time_shifts, 80)
        return percentile_80

    def to_dict(self):
        return {
            'wake_up_time': self.wake_up_time.strftime('%Y-%m-%d %H:%M:%S'),
            'sleep_at_time': self.sleep_at_time.strftime('%Y-%m-%d %H:%M:%S'),
            'msg_notify_time': self.msg_notify_time.strftime('%Y-%m-%d %H:%M:%S')
        }
