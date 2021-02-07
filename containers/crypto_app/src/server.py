import asyncio
import websockets

import os
import json
import boto3
import time
import re
from asgiref.sync import sync_to_async

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

    kinesis_records = []
    shard_count = 1
    async for message in websocket:
        message_dict = json.loads(message)
        # Only add messages related to the crypto subscriptions
        if int(message_dict["TYPE"]) in [0, 2, 5]:
            # Do custom processing on the payload here
            message = message + "\n"

            kinesis_record = {
                "Data": message,
                "PartitionKey": str(shard_count),
            }
            kinesis_records.append(kinesis_record)
            if len(kinesis_records) == 100:
                await publish_to_kinesis_stream(
                    kinesis_records, KINESIS_STREAM_NAME
                )
                kinesis_records = []
        # Cast to int and check for matching status error
        if int(message_dict["TYPE"]) == 429:
            # Wait 5 minutes for rate limiting
            time.sleep(300)
        # Regex for matching on 5xx errors or 401(unauthorized) error
        elif re.search(r"^5\d{2}$", message_dict["TYPE"]) or (
            int(message_dict["TYPE"]) == 401
        ):
            raise Exception(
                "Request returned an error: {} {}".format(
                    message_dict["TYPE"], message_dict
                )
            )


async def connect_to_websocket(url: str) -> None:
    async with websockets.connect(url) as websocket:
        await consumer_handler(websocket)


async def publish_to_kinesis_stream(
    kinesis_records: list, stream_name: str
) -> None:
    # if LOCAL_DEV:
    #     session = boto3.session.Session(
    #         aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    #         aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    #     )
    #     kinesis_client = session.client("kinesis", "us-east-2")
    # else:
    kinesis_client = boto3.client("kinesis", "us-east-1")

    print(kinesis_records)
    response = await sync_to_async(kinesis_client.put_records)(
        Records=kinesis_records,
        StreamName=stream_name,
    )
    return response


def main():
    api_key = auth()
    url = create_url(api_key)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_websocket(url))


if __name__ == "__main__":
    main()
