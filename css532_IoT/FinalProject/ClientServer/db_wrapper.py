import boto3
import uuid

class db_wrapper:
    def __init__(self):
        self.dynamoDB = boto3.resource('dynamodb')

    def insert_one_alarm(self, time, phone, repeat, prefer_sleep_time):
        table = self.dynamoDB.Table('ALARMS')
        id = str(uuid.uuid4())

        # Insert an item
        response = table.put_item(
            Item={
                'ID': id,
                'TIME': time,
                'PHONE': phone,
                'REPEAT': repeat,
                'PREFER_SLEEP_TIME': prefer_sleep_time
            }
        )
        return response, id

    def query_one_alarm(self, id):
        table = self.dynamoDB.Table('ALARMS')
        response = table.get_item(
            Key={
                'ID': id
            }
        )
        return response.get('Item')

    def delete_one_alarm(self, id):
        table = self.dynamoDB.Table('ALARMS')
        response = table.delete_item(
            Key={
                'ID': id
            }
        )

        return response

    def query_all_alarms(self):
        table = self.dynamoDB.Table('ALARMS')

        response = table.scan()
        results = response.get('Items', [])

        # Check if there are more items (pagination support)
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            results.extend(response.get('Items', []))

        return results

    def query_30_behaviors(self):
        table = self.dynamoDB.Table('BEHAVIORS')
        response = table.scan(
            Limit=30 # Limit the result to 30 records
        )
        results = response.get('Items', [])
        return results

