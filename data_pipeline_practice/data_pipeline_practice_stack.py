from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    # aws_elasticloadbalancingv2 as elbv2,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
    aws_ecr as ecr,
)


class DataPipelinePracticeStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "VPC")

        ecs_cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        ecr_repository = ecr.Repository.from_repository_name(
            self, "ecrRepository", repository_name="twitter-stream-app"
        )

        fargate_cluster = ecs_patterns.QueueProcessingFargateService(
            self,
            "FargateQueueProcessor",
            image=ecs.ContainerImage.from_ecr_repository(ecr_repository),
            cluster=ecs_cluster,
        )
