import os
from aws_cdk import (
    core,
    aws_kinesis as kinesis,
    aws_s3 as s3,
    aws_kinesisfirehose as kf,
    aws_iam as iam,
)

from aws_solutions_constructs import (
    aws_kinesis_streams_kinesis_firehose_s3 as kinesis_data_pipeline,
)

OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET")


class DataPipelineStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TO-DO: Resolve how to surface this through a property rather than directly.
        self.kinesis_stream = kinesis.Stream(
            self,
            "kinesisStream",
            retention_period=core.Duration.days(3),
            stream_name=core.PhysicalName.GENERATE_IF_NEEDED,
        )
        core.CfnOutput(
            self,
            "kinesisDataStreamArn",
            value=self.kinesis_stream.stream_arn,
        )

        bucket = s3.Bucket.from_bucket_name(
            self, "s3Bucket", bucket_name=OUTPUT_BUCKET
        )

        kf_role = iam.Role(
            self,
            "kinesisFirehoseRole",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )

        kf_props = kf.CfnDeliveryStreamProps(
            extended_s3_destination_configuration=kf.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                role_arn=kf_role.role_arn,
                bucket_arn=bucket.bucket_arn,
                prefix="twitter_data_",
                error_output_prefix="failures",
            )
        )

        data_pipeline = (
            kinesis_data_pipeline.KinesisStreamsToKinesisFirehoseToS3(
                self,
                "dataPipeline",
                existing_stream_obj=self.kinesis_stream,
                existing_bucket_obj=bucket,
                kinesis_firehose_props=kf_props,
            )
        )

        bucket.grant_write(data_pipeline.kinesis_firehose_role)
