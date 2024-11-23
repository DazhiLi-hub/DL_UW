from flask import Flask
from flask_restful import Api
from resources import AlarmSingleResource, AlarmListResource

app = Flask(__name__)
api = Api(app)

# Add resources (routes)
api.add_resource(AlarmListResource, '/alarms')        # GET all items
api.add_resource(AlarmSingleResource, '/alarms/<string:alarm_id>')  # GET, PUT, DELETE single item

if __name__ == '__main__':
    app.run(debug=True)
