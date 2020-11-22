#!/usr/bin/env python3

from aws_cdk import core

from data_pipeline_practice.data_pipeline_practice_stack import (
    DataPipelinePracticeStack,
)


app = core.App()
DataPipelinePracticeStack(app, "data-pipeline-practice")

app.synth()
