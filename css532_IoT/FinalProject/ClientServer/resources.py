from flask_restful import Resource
from flask import request
from datetime import datetime

from db_wrapper import db_wrapper, send_msg


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
        payload = request.get_json()
        # validation and set value
        try:
            datetime.strptime(payload.get('time'), "%H:%M")
        except ValueError:
            return {'message': 'Invalid time format. Please enter in HH:MM format.'}, 400
        if not payload.get('phone') or len(str(payload.get('phone'))) != 10:
            return {'message': 'Invalid phone number. Please enter valid 10 digits US phone number.'}, 400
        if payload.get('repeat') and payload.get('repeat') not in (True, False):
            return {'message': 'Invalid repeat type. Please enter True or False'}
        if payload.get('prefer_sleep_time') and not isinstance(payload.get('prefer_sleep_time'), int):
            return {'message': 'Invalid prefer_sleep_time. Please enter a valid number'}

        # Database manipulation
        db = db_wrapper()
        db_result, db_id = db.insert_one_alarm(time= payload.get('time'),
                            phone=payload.get('phone'),
                            repeat= True if payload.get('repeat') else False,
                            prefer_sleep_time=
                            payload.get('prefer_sleep_time') if payload.get('prefer_sleep_time') else 7)

        send_msg()

        if (db_result.get('ResponseMetadata').get('HTTPStatusCode') == 200):
            return {'message': 'alarm created. ID = ' + db_id}, 200
        else:
            return  {'message': 'inserting database failed'}