import os
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_kinesis as kinesis,
    aws_s3 as s3,
    aws_kinesisfirehose as kf,
    aws_iam as iam,
    aws_glue as glue,
)

from aws_solutions_constructs import (
    aws_kinesis_streams_kinesis_firehose_s3 as kinesis_data_pipeline,
)

from data_pipeline_practice.ecs_fargate_cluster import EcsFargateCluster

GLUE_DB_NAME = "blake_enyart_test_database"
GLUE_TABLE_NAME = "blake_enyart_twitter_data_2020"


class StreamingDataPipelineS3Stack(core.Stack):
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

        bucket = s3.Bucket.from_bucket_name(
            self, "S3Bucket", bucket_name="nutrien-blake-enyart-dev",
        )

        glue_db_arn = (
            f"arn:aws:glue:us-east-2:{self.account}:database/{GLUE_DB_NAME}"
        )
        glue_table_arn = f"arn:aws:glue:us-east-2:{self.account}:table/{GLUE_DB_NAME}/{GLUE_TABLE_NAME}"
        glue_catalog_arn = f"arn:aws:glue:us-east-2:{self.account}:catalog"

        glue_db = glue.Database.from_database_arn(
            self, "GlueDatabase", database_arn=glue_db_arn,
        )

        glue_table = glue.Table.from_table_arn(
            self, "GlueTable", table_arn=glue_table_arn,
        )

        kinesis_fh_role = iam.Role(
            self,
            "KinesisFirehoseS3Role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
            inline_policies={
                "GlueAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "glue:GetTable",
                                "glue:GetTableVersion",
                                "glue:GetTableVersions",
                            ],
                            resources=[
                                glue_db_arn,
                                glue_table_arn,
                                glue_catalog_arn,
                            ],
                            effect=iam.Effect.ALLOW,
                        )
                    ]
                )
            },
        )

        kinesis_fh_role.add_to_policy(
            statement=iam.PolicyStatement(
                actions=[
                    "s3:AbortMultipartUpload",
                    "s3:GetBucketLocation",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:PutObject",
                ],
                resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"],
                effect=iam.Effect.ALLOW,
            )
        )

        kinesis_firehose_props = kf.CfnDeliveryStreamProps(
            extended_s3_destination_configuration=kf.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                bucket_arn=bucket.bucket_arn,
                role_arn=kinesis_fh_role.role_arn,
                prefix="twitter_data_",
                compression_format="UNCOMPRESSED",
                buffering_hints=kf.CfnDeliveryStream.BufferingHintsProperty(
                    size_in_m_bs=64,
                ),
                encryption_configuration=kf.CfnDeliveryStream.EncryptionConfigurationProperty(
                    kms_encryption_config=kf.CfnDeliveryStream.KMSEncryptionConfigProperty(
                        awskms_key_arn=f"arn:aws:kms:us-east-2:{self.account}:alias/aws/s3"
                    )
                ),
                data_format_conversion_configuration=kf.CfnDeliveryStream.DataFormatConversionConfigurationProperty(
                    enabled=True,
                    input_format_configuration=kf.CfnDeliveryStream.InputFormatConfigurationProperty(
                        deserializer=kf.CfnDeliveryStream.DeserializerProperty(
                            open_x_json_ser_de=kf.CfnDeliveryStream.OpenXJsonSerDeProperty(
                                case_insensitive=True,
                                column_to_json_key_mappings={},
                                convert_dots_in_json_keys_to_underscores=True,
                            )
                        )
                    ),
                    output_format_configuration=kf.CfnDeliveryStream.OutputFormatConfigurationProperty(
                        serializer=kf.CfnDeliveryStream.SerializerProperty(
                            parquet_ser_de=kf.CfnDeliveryStream.ParquetSerDeProperty(
                                compression="GZIP",
                            )
                        )
                    ),
                    schema_configuration=kf.CfnDeliveryStream.SchemaConfigurationProperty(
                        database_name=glue_db.database_name,
                        role_arn=kinesis_fh_role.role_arn,
                        table_name=glue_table.table_name,
                        region="us-east-2",
                        version_id="LATEST",
                    ),
                ),
            )
        )

        data_pipeline = kinesis_data_pipeline.KinesisStreamsToKinesisFirehoseToS3(
            self,
            "MegaDataPipeline",
            existing_stream_obj=stream,
            existing_bucket_obj=bucket,
            kinesis_firehose_props=kinesis_firehose_props,
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
