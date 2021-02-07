import json
import pytest
from contextlib import asynccontextmanager
from asgiref.sync import sync_to_async
from containers.crypto_app.src.server import publish_to_kinesis_stream


@asynccontextmanager
async def kinesis_setup(kinesis_client):
    await sync_to_async(kinesis_client.create_stream)(
        StreamName="TestStream", ShardCount=1
    )
    yield


class TestCryptoAppServer:
    @pytest.mark.asyncio
    async def test_put_records(self, kinesis_client, kinesis_payload):
        """test the successful addition of an object to an existing kinesis stream"""
        async with kinesis_setup(kinesis_client):
            response = await publish_to_kinesis_stream(
                kinesis_payload, "TestStream"
            )

            assert response["FailedRecordCount"] == 0
