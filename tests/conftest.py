import boto3
import os
import pytest
import json
from moto import mock_kinesis, mock_sqs


@pytest.fixture(scope="module")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="module")
def kinesis_client(aws_credentials):
    with mock_kinesis():
        conn = boto3.client("kinesis", region_name="us-east-1")
        yield conn


@pytest.fixture(scope="module")
def kinesis_payload():
    """Mocked kinesis records for moto."""
    payload = {"Data": "test", "PartitionKey": "1"}
    payload_ls = [payload, payload, payload]
    return payload_ls
