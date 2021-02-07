import asyncio
import websockets

import os
import json
import boto3
import time

KINESIS_STREAM_NAME = os.environ.get("KINESIS_STREAM_NAME")
LOCAL_DEV = os.environ.get("LOCAL_DEV")


def auth():
    return os.environ.get("CRYPTO_COMPARE_API_KEY")


def create_url(api_key: str) -> None:
    return f"wss://streamer.cryptocompare.com/v2?api_key={api_key}"


async def consumer_handler(
    websocket: websockets.WebSocketClientProtocol,
) -> None:

    await websocket.send(
        json.dumps(
            {
                "action": "SubAdd",
                "subs": [
                    "5~CCCAGG~BTC~USD",
                    "0~Coinbase~ETH~USD",
                    "2~Binance~BTC~USDT",
                ],
            }
        )
    )

    async for message in websocket:
        await consumer(message)


async def connect_to_websocket(url: str) -> None:
    async with websockets.connect(url) as websocket:
        await consumer_handler(websocket)


async def consumer(message):
    print(message)


#     kinesis_records = []
#     shard_count = 1

#     for response_line in response.iter_lines():
#         if response_line:
#             str_response = response_line.decode("utf-8")
#             # Do custom processing on the payload here
#             str_response = str_response + "\n"

#             payload = str_response.encode("utf-8")

#             kinesis_record = {
#                 "Data": payload,
#                 "PartitionKey": str(shard_count),
#             }
#             kinesis_records.append(kinesis_record)
#             if len(kinesis_records) == 100:
#                 publish_to_kinesis_stream(kinesis_records, KINESIS_STREAM_NAME)
#                 kinesis_records = []
#     if response.status_code == 429:
#         # Wait 5 minutes for rate limiting
#         time.sleep(300)
#     elif response.status_code != 200:
#         raise Exception(
#             "Request returned an error: {} {}".format(
#                 response.status_code, response.text
#             )
#         )


# def publish_to_kinesis_stream(kinesis_records: list, stream_name: str):
#     if LOCAL_DEV:
#         session = boto3.session.Session(
#             aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
#             aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
#         )
#         kinesis_client = session.client("kinesis", "us-east-2")
#     else:
#         kinesis_client = boto3.client("kinesis", "us-east-2")

#     print(kinesis_records)
#     kinesis_client.put_records(
#         Records=kinesis_records,
#         StreamName=stream_name,
#     )


def main():
    api_key = auth()
    url = create_url(api_key)
    # headers = create_headers(bearer_token)
    # timeout = 0
    # while True:
    asyncio.get_event_loop().run_until_complete(connect_to_websocket(url))
    # timeout += 1


if __name__ == "__main__":
    main()
