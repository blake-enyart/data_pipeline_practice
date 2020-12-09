#!/usr/bin/env python3

from aws_cdk import core
import os

from data_pipeline_practice.streaming_data_pipeline_s3_stack import (
    StreamingDataPipelineS3Stack,
)


ORG_NAME = os.environ["ORG_NAME"]
PROJECT_NAME = os.environ["PROJECT_NAME"]
STAGE = os.environ["STAGE"]

app = core.App()
streaming_data_pipeline_s3_stack = StreamingDataPipelineS3Stack(
    app, "streaming-data-pipeline-s3"
)

core.Tags.of(streaming_data_pipeline_s3_stack).add(
    "Project", f"{ORG_NAME}-{PROJECT_NAME}-{STAGE}"
)

app.synth()
