from ddlgenerator.ddlgenerator import Table
import pandas as pd
import io
import csv

file_path = "/Users/bl9190033/Downloads/data-pipeline-practice-MegaDataPipelineKinesisFireh-ODItgGklWG78-8-2020-12-06-07-28-16-bef43b04-bcfb-4f26-92d2-804f97381591.parquet"
table_name = "test"
sql_dialect = "postgresql"


def parquet_to_sql_ddl(file_path: str, table_name: str, sql_dialect: str):
    f = io.StringIO()

    df = pd.read_parquet(file_path)
    data = df.to_dict("records")

    table = Table(data=data, table_name=table_name, uniques=True)
    sql = table.sql(sql_dialect, drops=False, metadata_source=True)

    with open(file="test.sql", mode="w") as output:
        output.write(sql)


if __name__ == "__main__":
    parquet_to_sql_ddl(file_path, table_name, sql_dialect)
