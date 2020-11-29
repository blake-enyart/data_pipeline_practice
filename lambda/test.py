import json


def handler(event, context):
    print("request: {}".format(json.dumps(event)))
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": "Hello from Lambda!",
        "headers": {"Content-Type": "application/json"},
    }
