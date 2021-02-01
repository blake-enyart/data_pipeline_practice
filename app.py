#!/usr/bin/env python3

from aws_cdk import core
import os
import getpass
from data_pipeline_practice.streaming_data_pipeline_s3_stack import (
    StreamingDataPipelineS3Stack,
)

USERNAME = getpass.getuser()

app = core.App()
streaming_data_pipeline_s3_stack = StreamingDataPipelineS3Stack(
    app, f"streaming-data-pipeline-s3-{USERNAME}"
)

app.synth()
