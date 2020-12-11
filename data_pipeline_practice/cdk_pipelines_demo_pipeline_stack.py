from aws_cdk import (
    aws_codepipeline as cpp,
    aws_codepipeline_actions as cpp_actions,
    core,
    pipelines,
)

import os

from data_pipeline_practice.cdk_pipelines_stage import MyApplication


class CdkPipelinesDemoStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        source_artifact = cpp.Artifact()
        cloud_assembly_artifact = cpp.Artifact()

        cicd_pipeline = pipelines.CdkPipeline(
            self,
            "DemoPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name="DemoPipeline",
            source_action=cpp_actions.GitHubSourceAction(
                action_name="GitHub",
                output=source_artifact,
                oauth_token=core.SecretValue.secrets_manager(
                    "github-token-blake-enyart"
                ),
                owner="blake-enyart",
                repo="data_pipeline_practice",
                branch="bte-pipeines-test",
            ),
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command="npm install -g aws-cdk",
                build_command="poetry install",
                synth_command="cdk synth",
            ),
        )

        cicd_pipeline.add_application_stage(
            app_stage=MyApplication(
                self,
                "MyApplication",
                env=core.Environment(
                    account="848684029682", region="us-east-2",
                ),
            ),
        )
