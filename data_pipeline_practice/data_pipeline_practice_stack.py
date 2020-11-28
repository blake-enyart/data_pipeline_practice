from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_kinesis as kinesis,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_logs as logs,
)

from aws_solutions_constructs import (
    aws_kinesis_streams_kinesis_firehose_s3 as kinesis_data_pipeline,
)


class DataPipelinePracticeStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stream = kinesis.Stream(
            self, "TwitterStreamStream", retention_period=core.Duration.days(3)
        )

        data_pipeline = kinesis_data_pipeline.KinesisStreamsToKinesisFirehoseToS3(
            self, "MegaDataPipeline", existing_stream_obj=stream
        )

        vpc = ec2.Vpc(self, "VPC", max_azs=2)

        ecs_task_role = iam.Role(
            self,
            "EcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="First pass role for ECS to publish to Kinesis",
        )

        stream.grant_read_write(ecs_task_role)

        ecs_cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        ecr_repository = ecr.Repository.from_repository_name(
            self, "ecrRepository", repository_name="twitter-stream-app"
        )

        twitter_credentials = secretsmanager.Secret.from_secret_name_v2(
            self,
            "TwitterCredentials",
            "BlakeEnyart/dev/dataPipelinePractice/TwitterAPI",
        )

        ecs_task_definition = ecs.FargateTaskDefinition(
            self, "FargateTaskDefinition", task_role=ecs_task_role,
        )

        lg = logs.LogGroup(self, "EcsLogGroup")
        log = ecs.AwsLogDriver(log_group=lg, stream_prefix="ecs",)

        ecs_container_definition = ecs.ContainerDefinition(
            self,
            "EcsContainer",
            image=ecs.ContainerImage.from_ecr_repository(ecr_repository),
            secrets={
                "TWITTER_API_KEY": ecs.Secret.from_secrets_manager(
                    twitter_credentials, "TWITTER_API_KEY"
                ),
                "TWITTER_SECRET_API_KEY": ecs.Secret.from_secrets_manager(
                    twitter_credentials, "TWITTER_SECRET_API_KEY"
                ),
                "TWITTER_BEARER_TOKEN": ecs.Secret.from_secrets_manager(
                    twitter_credentials, "TWITTER_BEARER_TOKEN"
                ),
                "TWITTER_ACCESS_TOKEN": ecs.Secret.from_secrets_manager(
                    twitter_credentials, "TWITTER_ACCESS_TOKEN"
                ),
                "TWITTER_SECRET_ACCESS_TOKEN": ecs.Secret.from_secrets_manager(
                    twitter_credentials, "TWITTER_SECRET_ACCESS_TOKEN"
                ),
            },
            environment={
                "KINESIS_STREAM_NAME": data_pipeline.kinesis_stream.stream_name
            },
            task_definition=ecs_task_definition,
            logging=log,
        )

        ecs.FargateService(
            self,
            "FargateService",
            task_definition=ecs_task_definition,
            cluster=ecs_cluster,
        )
