#!/usr/bin/env python3

from aws_cdk import core
import os

from data_pipeline_practice.data_pipeline_practice_stack import (
    DataPipelinePracticeStack,
)


ORG_NAME = os.environ["ORG_NAME"]
PROJECT_NAME = os.environ["PROJECT_NAME"]
STAGE = os.environ["STAGE"]

app = core.App()
data_pipeline_practice_stack = DataPipelinePracticeStack(
    app, "data-pipeline-practice"
)

core.Tags.of(data_pipeline_practice_stack).add(
    "Project", f"{ORG_NAME}-{PROJECT_NAME}-{STAGE}"
)

app.synth()
