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

# For development
default_env = core.Environment(
    region=os.getenv("CDK_DEFAULT_REGION"),
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
)

app = core.App()
networking_stack = NetworkingStack(
    app, f"networking-{USERNAME}-{STAGE}", env=default_env
)

data_pipeline_stack = DataPipelineStack(
    app, f"data-pipeline-{USERNAME}-{STAGE}", env=default_env
)

twitter_stream_app = TwitterStreamAppStack(
    app,
    f"twitter-stream-app-{USERNAME}-{STAGE}",
    env=default_env,
    vpc=networking_stack.vpc,
    kinesis_stream=data_pipeline_stack.kinesis_stream,
)
twitter_stream_app.add_dependency(data_pipeline_stack)

stacks = [networking_stack, data_pipeline_stack, twitter_stream_app]

# Add tags to multistack deployment
for stack in stacks:
    core.Tags.of(stack).add(
        key="projectName", value=f"DemoProject-{USERNAME}-{STAGE}"
    )

app.synth()
