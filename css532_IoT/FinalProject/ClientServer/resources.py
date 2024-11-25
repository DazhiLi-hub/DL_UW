import json

from flask_restful import Resource
from flask import request
from datetime import datetime

from db_wrapper import db_wrapper
from mqtt_wrapper import mqtt_wrapper
from time_schedule import time_schedule


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
                    "time": "HH:MM"(required)
                    "phone": "732-890-1811" (required)
                    "repeat": True(optional)
                    "prefer_sleep_time": "7" (optional)
                }
    """
    def post(self):
        # parse request body
        payload = request.get_json()
        wake_up_time = payload.get('time')
        phone = payload.get('phone')
        repeat = payload.get('repeat')
        prefer_sleep_time = payload.get('prefer_sleep_time')
        # validation and set value
        try:
            datetime.strptime(wake_up_time, "%H:%M")
        except ValueError:
            return {'message': 'Invalid time format. Please enter in HH:MM format.'}, 400
        if not phone or len(str(phone)) != 10:
            return {'message': 'Invalid phone number. Please enter valid 10 digits US phone number.'}, 400
        if repeat and repeat not in (True, False):
            return {'message': 'Invalid repeat type. Please enter True or False'}
        if prefer_sleep_time and not isinstance(prefer_sleep_time, int):
            return {'message': 'Invalid prefer_sleep_time. Please enter a valid number'}

        # Database manipulation
        db = db_wrapper()
        db_result, db_id = db.insert_one_alarm(time= payload.get('time'),
                            phone=phone,
                            repeat= True if repeat else False,
                            prefer_sleep_time= prefer_sleep_time if prefer_sleep_time else 7)
        if (db_result.get('ResponseMetadata').get('HTTPStatusCode') != 200):
            return {'message': 'inserting database failed'}

        # read user data and build time schedule
        # user_behaviors = [{'REAL_TIME': '2024-11-17 00:20:00', 'IDEAL_TIME': '2024-11-17 00:00:00'}]
        user_behaviors = db.query_30_behaviors()
        schedule = time_schedule(user_behaviors, wake_up_time, prefer_sleep_time)

        #sending time schedule to the IoT core
        mqtt = mqtt_wrapper()
        mqtt.publish_msg(json.dumps(schedule.to_dict()))


        return {'message': 'alarm created. ID = ' + db_id}, 200