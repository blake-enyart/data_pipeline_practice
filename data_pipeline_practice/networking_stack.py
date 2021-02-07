from aws_cdk import (
    core,
    aws_ec2 as ec2,
)


class NetworkingStack(core.Stack):
    @property
    def vpc(self):
        return self._vpc

    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._vpc = ec2.Vpc(self, "Vpc", max_azs=2)

        core.CfnOutput(self, "vpcId", value=self._vpc.vpc_id)
