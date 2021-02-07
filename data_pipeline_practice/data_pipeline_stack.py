import os
from aws_cdk import (
    core,
    aws_kinesis as kinesis,
    aws_s3 as s3,
    aws_kinesisfirehose as kf,
    aws_iam as iam,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
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

        bucket.grant_write(kf_role)

        # Cloudwatch alarm for stale data
        cloudwatch_alarm = cloudwatch.CfnAlarm(
            self,
            "CloudWatchAlarm",
            alarm_name="Stale Data Alarm",
            alarm_description="Notification that data has gone stale in the S3 bucket",
            actions_enabled=True,
            alarm_actions=[
                "arn:aws:sns:us-east-1:251357961920:dataPipelinePractice"
            ],
            metric_name="DeliveryToS3.DataFreshness",
            namespace="AWS/Firehose",
            statistic="Average",
            dimensions=[
                {
                    "name": "DeliveryStreamName",
                    "value": data_pipeline.kinesis_firehose.delivery_stream_name,
                }
            ],
            period=86400,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            threshold=86400,
            comparison_operator="GreaterThanThreshold",
            treat_missing_data="breaching",
        )

        snstopic = sns.CfnTopic(
            self,
            "SNSTopic",
            display_name="",
            topic_name="dataPipelinePractice",
        )

        snstopicpolicy = sns.CfnTopicPolicy(
            self,
            "SNSTopicPolicy",
            policy_document='{"Version":"2008-10-17","Id":"__default_policy_ID","Statement":[{"Sid":"__default_statement_ID","Effect":"Allow","Principal":{"AWS":"*"},"Action":["SNS:GetTopicAttributes","SNS:SetTopicAttributes","SNS:AddPermission","SNS:RemovePermission","SNS:DeleteTopic","SNS:Subscribe","SNS:ListSubscriptionsByTopic","SNS:Publish","SNS:Receive"],"Resource":"arn:aws:sns:us-east-1:251357961920:dataPipelinePractice","Condition":{"StringEquals":{"AWS:SourceOwner":"251357961920"}}}]}',
            topics=[snstopic.ref],
        )

        snssubscription = sns.CfnSubscription(
            self,
            "SNSSubscription",
            topic_arn=snstopic.ref,
            endpoint="blake.enyart@gmail.com",
            protocol="email",
            region="us-east-1",
        )
