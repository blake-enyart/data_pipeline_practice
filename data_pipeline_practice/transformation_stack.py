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
