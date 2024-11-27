import boto3

class db_wrapper:
    def __init__(self):
        self.dynamoDB = boto3.resource('dynamodb')

    def insert_one_behavior(self, real_time, ideal_time):
        table = self.dynamoDB.Table('BEHAVIORS')

        # Insert an item
        response = table.put_item(
            Item={
                'REAL_TIME': real_time,
                'IDEAL_TIME': ideal_time
            }
        )
        return response
