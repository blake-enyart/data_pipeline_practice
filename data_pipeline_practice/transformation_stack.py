from aws_cdk import (
    core,
)


class TransformationStack(core.Stack):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        glue_db_arn = f"arn:aws:glue:us-east-2:{AWS_ACCOUNT_NUMBER}:database/{GLUE_DB_NAME}"

        glue_table_arn = f"arn:aws:glue:us-east-2:{AWS_ACCOUNT_NUMBER}:table/{GLUE_DB_NAME}/{GLUE_TABLE_NAME}"
        glue_catalog_arn = (
            f"arn:aws:glue:us-east-2:{AWS_ACCOUNT_NUMBER}:catalog"
        )

        glue_db = glue.Database.from_database_arn(
            self,
            "GlueDatabase",
            database_arn=glue_db_arn,
        )

        glue_table = glue.Table.from_table_arn(
            self,
            "GlueTable",
            table_arn=glue_table_arn,
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
                ),
                "S3Access": iam.PolicyStatement(
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
                ),
            },
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
                        awskms_key_arn=f"arn:aws:kms:us-east-2:{AWS_ACCOUNT_NUMBER}:alias/aws/s3"
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
