from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_kinesis as kinesis,
)

from aws_solutions_constructs import (
    aws_kinesis_streams_kinesis_firehose_s3 as kinesis_data_pipeline,
)

from data_pipeline_practice.ecs_fargate_cluster import EcsFargateCluster


class DataPipelinePracticeStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stream = kinesis.Stream(
            self, "TwitterStreamStream", retention_period=core.Duration.days(3)
        )
        core.CfnOutput(
            self, "KinesisDataStreamName", value=stream.stream_name,
        )

        data_pipeline = kinesis_data_pipeline.KinesisStreamsToKinesisFirehoseToS3(
            self, "MegaDataPipeline", existing_stream_obj=stream
        )

        vpc = ec2.Vpc(self, "VPC", max_azs=2)

        ecs_cluster = EcsFargateCluster(
            self,
            "EcsFargateCluster",
            vpc=vpc,
            ecr_repo_name="twitter-stream-app",
            data_pipeline=data_pipeline,
        )

        stream.grant_read_write(ecs_cluster.ecs_task_role)
