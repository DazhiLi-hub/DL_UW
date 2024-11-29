import json

from flask_restful import Resource
from flask import request
from datetime import datetime, timedelta

from db_wrapper import db_wrapper
from mqtt_wrapper import mqtt_wrapper
from time_schedule import time_schedule

TIME_SCHEDULE_TOPIC = 'system/time_schedule'
CANCEL_SCHEDULE_TOPIC = 'system/cancel_schedule'

class AlarmSingleResource(Resource):

    """
    query single alarm by alarm_id
    """
    def get(self, alarm_id):
        db = db_wrapper()
        result = db.query_one_alarm(alarm_id)
        return str(result), 200

    """
    modify one alarm, not implemented here
    """
    def put(self, alarm_id):
        return {'message': 'Not supported method. Please delete and create a new alarm'}, 501

    """
    delete one alarm by id
    """
    def delete(self, alarm_id):
        db = db_wrapper()
        db.delete_one_alarm(alarm_id)
        mqtt = mqtt_wrapper()
        mqtt.publish_msg(CANCEL_SCHEDULE_TOPIC, json.dumps({'id': alarm_id}))
        return {'message': 'id=' + alarm_id + ' is deleted successfully'}, 200



class AlarmListResource(Resource):
    """
    Query All alarms in the database
    """
    def get(self):
        db = db_wrapper()
        results = db.query_all_alarms()
        return str(results), 200

    """
                Create an alarm clock by posting a form of info
                ReqBody:
                {
                    "time": "8:20",
                    "phone": "+12067329811",
                    "prefer_sleep_time": 8
                }
    """
    def post(self):
        # parse request body
        payload = request.get_json()
        wake_up_time = payload.get('time')
        phone = payload.get('phone')
        prefer_sleep_time = payload.get('prefer_sleep_time')
        # validation and set value
        try:
            datetime.strptime(wake_up_time, "%H:%M")
        except ValueError:
            return {'message': 'Invalid time format. Please enter in HH:MM format.'}, 400
        if not phone or len(phone) != 12 or not phone.startswith("+1"):
            return {'message': 'Invalid phone number. Please enter valid 10 digits US phone number begin with +1.'}, 400
        if prefer_sleep_time and not isinstance(prefer_sleep_time, int):
            return {'message': 'Invalid prefer_sleep_time. Please enter a valid number'}

        # transforming wake up time to exact datetime
        now = datetime.now()
        target_time = now.replace(hour=int(wake_up_time.split(':')[0]),
                                  minute=int(wake_up_time.split(':')[1]),
                                  second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        wake_up_time = target_time

        # Database manipulation
        db = db_wrapper()

        # check target date has a schedule, currently supports only one schedule for a day

        # inserting data into db
        db_result, db_id = db.insert_one_alarm(date= wake_up_time.date().strftime("%Y-%m-%d"),
                                               time= wake_up_time.time().strftime("%H:%M:%S"),
                                               phone=phone,
                                               prefer_sleep_time= prefer_sleep_time if prefer_sleep_time else 7)
        if (db_result.get('ResponseMetadata').get('HTTPStatusCode') != 200):
            return {'message': 'inserting database failed'}

        # read user data and build time schedule
        # user_behaviors = [{'REAL_TIME': '2024-11-17 00:20:00', 'IDEAL_TIME': '2024-11-17 00:00:00'}]
        user_behaviors = db.query_30_behaviors()
        schedule = time_schedule(user_behaviors, wake_up_time, prefer_sleep_time)

        #sending time schedule to the IoT core
        mqtt = mqtt_wrapper()
        msg_payload = schedule.to_dict()
        msg_payload["to_phone_number"] = phone
        msg_payload["id"] = db_id
        mqtt.publish_msg(TIME_SCHEDULE_TOPIC, json.dumps(msg_payload))


        return {'message': 'alarm created. ID = ' + db_id}, 200