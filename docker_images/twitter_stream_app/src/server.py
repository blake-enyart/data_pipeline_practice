import requests
import os
import json
import boto3
import botocore

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
KINESIS_STREAM_NAME = os.environ.get(
    "KINESIS_STREAM_NAME",
    "data-pipeline-practice-TwitterStreamStream0A60CA48-7ECBF21U9SWL",
)


def auth():
    return os.environ.get("TWITTER_BEARER_TOKEN")


def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream"


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    params = {
        "tweet.fields": "created_at,public_metrics,geo",
        "expansions": "author_id,geo.place_id",
        "user.fields": "created_at",
    }

    response = requests.request(
        "GET", url, headers=headers, stream=True, params=params
    )
    print(response.status_code)
    kinesis_records = []
    shard_count = 1

    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            kinesis_record = {
                "Data": response_line,
                "PartitionKey": str(shard_count),
            }
            kinesis_records.append(kinesis_record)
            if len(kinesis_records) == 5:
                publish_to_kinesis_stream(kinesis_records, KINESIS_STREAM_NAME)
                kinesis_records = []
            print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def publish_to_kinesis_stream(kinesis_records: list, stream_name: str):
    session = boto3.session.Session(profile_name="nutrien")
    kinesis_client = session.client("kinesis", "us-east-2")
    kinesis_client.put_records(
        Records=kinesis_records, StreamName=stream_name,
    )


def main():
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    timeout = 0
    while True:
        connect_to_endpoint(url, headers)
        timeout += 1


if __name__ == "__main__":
    main()
