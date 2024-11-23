import os
import json
import asyncio
import time
import random

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

model_id = "Dazhi'sDesktop"

"""
This method generating temperature messages
randomly generated a list of 5 temperature with timestamp
the timestamp should be now, now-1minute ..... now-4minute
"""
def generate_msg():
    telemetry_msg = {'result': []}
    for i in range(5):
        # telemetry_msg['result'].insert(0,
        #     {'timestamp':now, 'temperature': random.randrange(0, 50)}
        # )
        # now-=60
        telemetry_msg['result'].append(random.randrange(0, 50))
    msg = Message(json.dumps(telemetry_msg))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    return msg

async def main():
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    print("Connecting using Connection String")
    device_client = IoTHubDeviceClient.create_from_connection_string(
        conn_str, product_info=model_id
    )

    await device_client.connect()
    # generating messages
    sent_msg = generate_msg()
    print("Sending message...")
    print(sent_msg)
    await device_client.send_message(sent_msg)
    print("Message successfully sent!")

    await device_client.shutdown()


if __name__ == '__main__':
    asyncio.run(main())