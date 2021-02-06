#!/usr/bin/env python3

from aws_cdk import core
import os
import getpass

from data_pipeline_practice.data_pipeline_stack import (
    DataPipelineStack,
)

from data_pipeline_practice.networking_stack import (
    NetworkingStack,
)

from data_pipeline_practice.twitter_stream_app_stack import (
    TwitterStreamAppStack,
)

USERNAME = getpass.getuser()
STAGE = os.getenv("STAGE", "dev")

app = core.App()
networking_stack = NetworkingStack(app, f"networking-{USERNAME}-{STAGE}")

data_pipeline_stack = DataPipelineStack(
    app,
    f"streaming-data-pipeline-s3-{USERNAME}-{STAGE}",
    env={"OUTPUT_BUCKET": "blake-enyart-dev"},
)

twitter_stream_app = TwitterStreamAppStack(
    app,
    f"twitter-stream-app-{USERNAME}-{STAGE}",
)

app.synth()
