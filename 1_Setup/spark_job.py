import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, sum
from datetime import datetime

def main() :
    raw_data_dir = sys.argv[1]
    aurora_endpoint = sys.argv[2]

    spark = SparkSession.builder.appName("Test").getOrCreate()

    df = spark.read.format("parquet")\
        .option("inferSchema", "true")\
        .option("mode", "failFast")\
        .load(raw_data_dir)\
        .coalesce(5)

    total_quantity = df.agg(sum("Quantity"))
    total_quantity = total_quantity.withColumn('date',lit(datetime.now().strftime("%Y-%m-%d")))
    total_quantity = total_quantity.withColumnRenamed('sum(Quantity)', 'value')

    jdbc_url = f'jdbc:mysql://{aurora_endpoint}:3306/airflow'
    connection_properties = {
        "user": "admin",
        "password": "Administrator",
        "driver": "com.mysql.jdbc.Driver"  # 사용하는 JDBC 드라이버에 맞게 변경해야 합니다.
    }

    total_quantity.coalesce(1).write.jdbc(url=jdbc_url, table="emr_table", mode="append", properties=connection_properties)

    spark.stop()
    
if __name__ == '__main__' :
	main()

