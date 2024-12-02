# Sleeping Habit Forming Alarm Clock

## Client Server Setup

Library Dependencies:

1. boto3
2. botocore
3. Flask
4. Flask-RESTful
5. AWSCRT
6. AWSIOTSDK

How to run codes:

1. Add a thing on AWS IoT core and download related credencials(pricate key, cert etc.) to send MQTT message
2. Set policy to thing, allow thing to user client-id: client server
3. Set policy to thing, allow thing to push messages on topics: system/time-schedule, system/cancel-schedule

## Alarm Clock Setup
Library Dependencies:
1. GPIO etc.
2. boto3
3. botocore
4. twilio
5. AWSCRT
6. AWSIOTSDK

How to run code:
1. The same as client server, however, allow thing to subscribe on topics: system/time-schedule, system/cancel-schedule
2. Register an account on twilio (same as AWS End user messaging service)
3. Add twilio account SID and token and originator phone number to system variables

## Database Setup
Tables:
1. ALARMS (ID(String)---DATE---PHONE---PREFER_SLEEP_TIME---TIME)
2.BEHAVIORS (REAL_TIME (String)---NOTIFY_TIME)

Install AWS CLI and set AWS account credencials. Prefer using AWS role attached with database access policy