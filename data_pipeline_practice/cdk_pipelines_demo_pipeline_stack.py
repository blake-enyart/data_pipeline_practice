from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    core,
    pipelines,
)

import os

from data_pipeline_practice.cdk_pipelines_stage import MyApplication


class CdkPipelinesDemoStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        source_artifact = cp.Artifact()
        cloud_assembly_artifact = cp.Artifact()

        cicd_pipeline = pipelines.CdkPipeline(
            self,
            "DemoPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name="DemoPipeline",
            source_action=cp_actions.GitHubSourceAction(
                action_name="GitHub",
                output=source_artifact,
                oauth_token=core.SecretValue.secrets_manager(
                    "github-token-blake-enyart"
                ),
                owner="blake-enyart",
                repo="data_pipeline_practice",
                branch="main",
            ),
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_command="npm install -g aws-cdk@1.75.0",
                build_commands=[
                    "pip install poetry",
                    "poetry config virtualenvs.create false",
                    "poetry install --no-dev",
                ],
                synth_command="cdk synth",
            ),
        )

        dev_stage = cicd_pipeline.add_application_stage(
            app_stage=MyApplication(
                self,
                "PreProd",
                env=core.Environment(
                    account="848684029682", region="us-east-2",
                ),
            ),
        )

        dev_stage.add_actions(
            pipelines.ShellScriptAction(
                action_name="TestService",
                commands=["pytest",],
                additional_artifacts=[cloud_assembly_artifact],
                run_order=3,
            ),
        )

        dev_stage.add_manual_approval_action("ManualApproval", run_order=4)

        cicd_pipeline.add_application_stage(
            app_stage=MyApplication(
                self,
                "Prod",
                env=core.Environment(
                    account="848684029682", region="us-east-1",
                ),
            ),
        )
