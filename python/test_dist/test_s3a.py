import os
import signal
import subprocess

import boto3
from pyspark import SparkConf
from pyspark.sql import SparkSession
import df_tests

# start moto server as a standalone process that can be accessed from the spark jvm process
# by default it runs on localhost on port 5000
process = subprocess.Popen(
    "moto_server s3", stdout=subprocess.PIPE,
    shell=True, preexec_fn=os.setsid
)

try:
    print("Create bucket")
    conn = boto3.resource("s3",
                          endpoint_url="http://127.0.0.1:5000",
                          aws_access_key_id="dummy",
                          aws_secret_access_key="dummy")
    conn.create_bucket(Bucket="test-bucket")

    # create a local spark session
    conf = SparkConf() \
        .setMaster("local[*]") \
        .setAppName("test") \
        .set("spark.ui.enabled", "false") \
        .set("spark.driver.host", "localhost")

    # use the moto s3 mock server and configure features it doesn't support
    # see https://hadoop.apache.org/docs/current/hadoop-aws/tools/hadoop-aws/troubleshooting_s3a.html
    conf.set("spark.hadoop.fs.s3a.endpoint", "http://127.0.0.1:5000") \
        .set("spark.hadoop.fs.s3a.multiobjectdelete.enable", "false") \
        .set("spark.hadoop.fs.s3a.access.key", "dummy") \
        .set("spark.hadoop.fs.s3a.secret.key", "dummy") \
        .set("spark.hadoop.fs.s3a.signing-algorithm", "S3SignerType")

    # use s3a for s3:// urls
    conf.set("spark.hadoop.fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    # use the new staging directory committer
    conf.set("spark.hadoop.mapreduce.outputcommitter.factory.scheme.s3a",
             "org.apache.hadoop.fs.s3a.commit.S3ACommitterFactory") \
        .set("spark.sql.sources.commitProtocolClass", "org.apache.spark.internal.io.cloud.PathOutputCommitProtocol") \
        .set("spark.sql.parquet.output.committer.class",
             "org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter") \
        .set("spark.hadoop.fs.s3a.committer.name", "directory") \
        .set("spark.hadoop.fs.s3a.committer.tmp.path", "file:///tmp/spark.staging")

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    # create a pyspark dataframe
    values = [("k1", 1), ("k2", 2)]
    columns = ["key", "value"]
    df1 = spark.createDataFrame(values, columns)

    df1.show()

    # write the dataframe as csv to s3
    df1.write.parquet("s3://test-bucket/data/")

    # read the dataset from s3
    df2 = spark.read.parquet("s3://test-bucket/data/")

    print("Check dataframes are equal")
    df_tests.assertDataFrameEqual(df1, df2)


finally:
    print("Shut down moto server")
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
