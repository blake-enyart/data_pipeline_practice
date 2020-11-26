from aws_cdk import (
    aws_s3 as s3,
    core,
    aws_apigatewayv2_integrations as apigw_int,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigw,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
)


class DataPipelinePracticeStack(core.Stack):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "VPC")
        alb = elbv2.ApplicationLoadBalancer(self, "ALB", vpc=vpc)

        ecs_cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        fargate_cluster = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ALBFargate",
            load_balancer=alb,
            cpu=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(
                    "amazon/amazon-ecs-sample"
                )
            ),
            memory_limit_mib=2048,
            public_load_balancer=False,
            cluster=ecs_cluster,
        )

        http_api = apigw.HttpApi(
            self,
            "HttpApi",
            default_integration=apigw_int.HttpAlbIntegration(
                listener=fargate_cluster.listener
            ),
        )
