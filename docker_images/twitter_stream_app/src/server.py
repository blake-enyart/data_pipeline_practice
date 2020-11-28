import requests
import os
import json
import boto3

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
    batch_payload = []
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            batch_payload.append(json_response)
            print(batch_payload)
            if len(batch_payload) == 5:
                publish_to_kinesis_stream(batch_payload, KINESIS_STREAM_NAME)
                batch_payload = []
            print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def publish_to_kinesis_stream(batch_payload: list, stream_name: str):
    kinesis_client = boto3.client("kinesis")
    kinesis_client.put_records(
        Records=batch_payload, StreamName=stream_name,
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
