import os
from aws_cdk import (
    core,
    aws_kinesis as kinesis,
    aws_s3 as s3,
)

from aws_solutions_constructs import (
    aws_kinesis_streams_kinesis_firehose_s3 as kinesis_data_pipeline,
)

OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "blake-enyart-dev")


class DataPipelineStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stream = kinesis.Stream(
            self, "kinesisStream", retention_period=core.Duration.days(3)
        )
        core.CfnOutput(
            self,
            "kinesisDataStreamArn",
            value=stream.stream_arn,
        )

        bucket = s3.Bucket.from_bucket_name(
            self, "s3Bucket", bucket_name=OUTPUT_BUCKET
        )

        data_pipeline = (
            kinesis_data_pipeline.KinesisStreamsToKinesisFirehoseToS3(
                self,
                "dataPipeline",
                existing_stream_obj=stream,
                existing_bucket_obj=bucket,
            )
        )
