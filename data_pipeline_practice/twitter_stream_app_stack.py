import os
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_logs as logs,
    aws_kinesis as kinesis,
)

# ECR_REPO_NAME = os.getenv("ECR_REPO_NAME", "twitter-stream-app")
TWITTER_SECRET_ARN = os.getenv("TWITTER_SECRET_ARN")
# VPC_ID = os.getenv("VPC_ID", "vpc-0363aa9349f902c07")
# KINESIS_STREAM_ARN = os.getenv("KINESIS_STREAM_ARN")


class TwitterStreamAppStack(core.Stack):
    @property
    def ecs_task_role(self):
        return self._ecs_task_role

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        vpc: ec2.IVpc,
        kinesis_stream: kinesis.IStream,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self._ecs_task_role = iam.Role(
            self,
            "ecsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="ECS Task Definition role to publish to Kinesis Data Stream",
        )

        twitter_credentials = secretsmanager.Secret.from_secret_complete_arn(
            self,
            "twitterCredentials",
            secret_complete_arn=TWITTER_SECRET_ARN,
        )

        ecs_cluster = ecs.Cluster(self, "ecsCluster", vpc=vpc)

        ecs_task_definition = ecs.FargateTaskDefinition(
            self,
            "fargateTaskDefinition",
            task_role=self._ecs_task_role,
        )

        ecs.ContainerDefinition(
            self,
            "ecsContainer",
            image=ecs.ContainerImage.from_asset(
                directory="containers/twitter_stream_app",
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
            environment={"KINESIS_STREAM_NAME": kinesis_stream.stream_name},
            task_definition=ecs_task_definition,
            logging=ecs.LogDriver.aws_logs(stream_prefix="ecs"),
        )

        ecs.FargateService(
            self,
            "fargateService",
            task_definition=ecs_task_definition,
            cluster=ecs_cluster,
        )

        kinesis_stream.grant_read_write(ecs_task_definition.task_role)
