from aws_cdk import core

from data_pipeline_practice.streaming_data_pipeline_s3_stack import (
    StreamingDataPipelineS3Stack,
)


class MyApplication(core.Stage):
    def __init__(
        self, scope: core.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        service = StreamingDataPipelineS3Stack(self, "StreamingDataPipeline")
