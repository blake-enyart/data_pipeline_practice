#!/usr/bin/env python3

from aws_cdk import core
import os

from data_pipeline_practice.streaming_data_pipeline_s3_stack import (
    StreamingDataPipelineS3Stack,
)
from data_pipeline_practice.cdk_pipelines_demo_pipeline_stack import (
    CdkPipelinesDemoStack,
)


ORG_NAME = os.getenv("ORG_NAME")
PROJECT_NAME = os.getenv("PROJECT_NAME")
STAGE = os.getenv("STAGE")

app = core.App()
# streaming_data_pipeline_s3_stack = StreamingDataPipelineS3Stack(
#     app, "streaming-data-pipeline-s3"
# )

cdk_pipelines_demo_pipeline_stack = CdkPipelinesDemoStack(
    app,
    "cdk-pipelines-demo-stack",
    env=core.Environment(
        account="848684029682", region=os.getenv("AWS_DEFAULT_REGION"),
    ),
)


app.synth()
