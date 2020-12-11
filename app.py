#!/usr/bin/env python3

from aws_cdk import core
import os
import getpass
from data_pipeline_practice.streaming_data_pipeline_s3_stack import (
    StreamingDataPipelineS3Stack,
)
from data_pipeline_practice.cdk_pipelines_demo_pipeline_stack import (
    CdkPipelinesDemoStack,
)


USERNAME = os.getenv("USERNAME")
# ORG_NAME = os.getenv("ORG_NAME")
# PROJECT_NAME = os.getenv("PROJECT_NAME")

app = core.App()
streaming_data_pipeline_s3_stack = StreamingDataPipelineS3Stack(
    app, f"streaming-data-pipeline-s3-{USERNAME}"
)

cdk_pipelines_demo_pipeline_stack = CdkPipelinesDemoStack(
    app,
    "cdk-deployment-pipeline",
    env=core.Environment(account="848684029682", region="us-east-2",),
)

app.synth()
