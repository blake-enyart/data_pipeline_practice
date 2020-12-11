import json
import pytest

from aws_cdk import core
from data_pipeline_practice.streaming_data_pipeline_s3_stack import (
    StreamingDataPipelineS3Stack,
)


def get_template():
    app = core.App()
    StreamingDataPipelineS3Stack(app, "streaming-data-pipeline-s3")
    return json.dumps(
        app.synth().get_stack_by_name("streaming-data-pipeline-s3").template
    )


def test_kinesis_streams_created():
    assert "AWS::KinesisFirehose::DeliveryStream" in get_template()


def test_kinesis_firehose_role_created():
    assert "AWS::IAM::Role" in get_template()
