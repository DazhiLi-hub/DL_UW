import json
import boto3

bucket = "iot-hw1"

def lambda_handler(event, context):
    # TODO implement
    json_event = json.loads(event)
    temperatures = json_event['temperatures']
    num_tem = len(temperatures)
    total = sum(temperatures)
    avg = total / num_tem

    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket=bucket, Key="raw/raw_data.txt", Body=str(temperatures))
    s3_client.put_object(Bucket=bucket, Key="avg/avg_data.txt", Body=str(avg))

    return {
        'statusCode': 200,
        'body': avg
    }