from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_logs as logs,
)

from aws_solutions_constructs import (
    aws_kinesis_streams_kinesis_firehose_s3 as kinesis_data_pipeline,
)


class EcsFargateCluster(core.Construct):
    @property
    def ecs_task_role(self):
        return self._ecs_task_role

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        vpc: ec2.IVpc,
        ecr_repo_name: str,
        data_pipeline: kinesis_data_pipeline,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self._ecs_task_role = iam.Role(
            self,
            "EcsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="ECS Task Definition role to publish to Kinesis Data Stream",
        )

        ecs_cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        twitter_credentials = secretsmanager.Secret.from_secret_complete_arn(
            self,
            "TwitterCredentials",
            secret_complete_arn="arn:aws:secretsmanager:us-east-2:848684029682:secret:BlakeEnyart/dev/dataPipelinePractice/TwitterAPI-JqFPsv",
        )

        ecs_task_definition = ecs.FargateTaskDefinition(
            self, "FargateTaskDefinition", task_role=self._ecs_task_role,
        )

        lg = logs.LogGroup(self, "EcsLogGroup")
        log = ecs.AwsLogDriver(log_group=lg, stream_prefix="ecs",)

        ecs_container_definition = ecs.ContainerDefinition(
            self,
            "EcsContainer",
            image=ecs.ContainerImage.from_asset(
                "docker_images/twitter_stream_app"
            ),
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
