import os
from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_kinesisfirehose as kf,
)


class MonitoringStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        kinesis_firehose: kf.CfnDeliveryStream,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Cloudwatch alarm for stale data
        snstopic = sns.Topic(
            self,
            "SNSTopic",
        )

        snstopicpolicy = sns.CfnTopicPolicy(
            self,
            "SNSTopicPolicy",
            policy_document={
                "Version": "2008-10-17",
                "Id": "__default_policy_ID",
                "Statement": [
                    {
                        "Sid": "__default_statement_ID",
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": [
                            "SNS:GetTopicAttributes",
                            "SNS:SetTopicAttributes",
                            "SNS:AddPermission",
                            "SNS:RemovePermission",
                            "SNS:DeleteTopic",
                            "SNS:Subscribe",
                            "SNS:ListSubscriptionsByTopic",
                            "SNS:Publish",
                            "SNS:Receive",
                        ],
                        "Resource": snstopic.topic_arn,
                        "Condition": {
                            "StringEquals": {"AWS:SourceOwner": self.account}
                        },
                    }
                ],
            },
            topics=[snstopic.topic_arn],
        )

        snstopic.add_subscription(
            subscriptions.EmailSubscription(
                email_address="blake.enyart@gmail.com",
            )
        )

        cloudwatch_alarm = cloudwatch.CfnAlarm(
            self,
            "CloudWatchAlarm",
            alarm_name="Stale Data Alarm",
            alarm_description="Notification that data has gone stale in the S3 bucket",
            actions_enabled=True,
            alarm_actions=[snstopic.topic_arn],
            metric_name="DeliveryToS3.DataFreshness",
            namespace="AWS/Firehose",
            statistic="Average",
            dimensions=[
                {
                    "name": "DeliveryStreamName",
                    "value": kinesis_firehose.ref,
                }
            ],
            period=86400,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            threshold=86400,
            comparison_operator="GreaterThanThreshold",
            treat_missing_data="breaching",
        )
