resource "aws_s3_bucket" "raw_data_bucket" {
  bucket = "${var.accountID}-bucket"
}

resource "aws_s3_object" "raw_data" {
  bucket = aws_s3_bucket.raw_data_bucket.id
  key    = "raw_data.parquet"
  source = "raw_data.parquet"

  depends_on = [ aws_s3_bucket.raw_data_bucket ]
}

resource "aws_s3_object" "dag" {
  bucket = aws_s3_bucket.raw_data_bucket.id
  key    = "EMR_DAG.py"
  source = "EMR_DAG.py"

  depends_on = [ aws_s3_bucket.raw_data_bucket ]
}

resource "aws_s3_object" "pyspark" {
  bucket = aws_s3_bucket.raw_data_bucket.id
  key    = "spark_job.py"
  source = "spark_job.py"

  depends_on = [ aws_s3_bucket.raw_data_bucket ]
}

resource "aws_s3_object" "mysql_jar" {
  bucket = aws_s3_bucket.raw_data_bucket.id
  key    = "mysql-connector-j-8.3.0.jar"
  source = "mysql-connector-j-8.3.0.jar"

  depends_on = [ aws_s3_bucket.raw_data_bucket ]
}