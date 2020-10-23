# Tekumara build of Apache PySpark with Hadoop 3.x

A build of Apache PySpark that uses the hadoop-cloud maven profile to bundle [hadoop-aws 3.x](https://hadoop.apache.org/docs/r3.2.0/hadoop-aws/tools/hadoop-aws/index.html) which contains S3A. 

## Install

See [Releases](https://github.com/tekumara/spark/releases)

## Usage
 
To use pyspark with temporary STS credentials:

```
pyspark --driver-java-options "-Dspark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider"
```

To modify an existing spark session to use S3A for S3 urls, for example `spark` in the pyspark shell:

```
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
```

See [test_s3a.py](https://github.com/tekumara/spark/blob/spark-cloud/python/test_dist/test_s3a.py#L43) for an example of using the staging committers.

## Rationale

The [pyspark distribution on pypi](https://pypi.org/project/pyspark/) ships with hadoop 2.7 and no cloud jars (ie: hadoop-aws).
So common practice is to use hadoop-aws 2.7.3 as follows:

```
pyspark --packages "org.apache.hadoop:hadoop-aws:2.7.3" --driver-java-options "-Dspark.hadoop.fs.s3.impl=org.apache.hadoop.fs.s3a.S3AFileSystem"
```

However, later versions of hadoop-aws cannot be used this way without errors.

This project [builds a pyspark distribution](https://github.com/tekumara/spark/blob/spark-cloud/.github/workflows/spark-cloud.yml#L59) from source with Hadoop 3.x.

Later versions of hadoop-aws contain the following new features:

* [2.8 release line](http://hadoop.apache.org/docs/r2.8.0/index.html) contains S3A improvements to support any AWSCredentialsProvider
* [2.9 release line](http://hadoop.apache.org/docs/r2.9.0/index.html) contains [S3Guard](http://hadoop.apache.org/docs/r2.9.0/hadoop-aws/tools/hadoop-aws/s3guard.html) which provides consistency and metadata caching for S3A via a backing DynamoDB metadata store.
* [3.1 release line](http://hadoop.apache.org/docs/r3.1.0/index.html) incorporates HADOOP-13786 which contains optimised job committers including the Netflix staging committers (Directory and Partitioned) and the Magic committers. See [committers](https://github.com/apache/hadoop/blob/branch-3.1/hadoop-tools/hadoop-aws/src/site/markdown/tools/hadoop-aws/committers.md) and [committer architecture](https://github.com/apache/hadoop/blob/trunk/hadoop-tools/hadoop-aws/src/site/markdown/tools/hadoop-aws/committer_architecture.md).
* [3.2 release line](http://hadoop.apache.org/docs/r3.2.0/index.html) an [enhanced S3A connector and S3Guard](https://issues.apache.org/jira/browse/HADOOP-15226?jql=project%20%3D%20HADOOP%20AND%20component%20%3D%20%22fs%2Fs3%22%20AND%20fixVersion%20%3D%203.2.0), including better resilience to throttled AWS S3 and DynamoDB IO.

To take advantage of the 3.x release line committers in Spark you also need the binding classes introduced into Spark 3.0.0 by [SPARK-23977](https://issues.apache.org/jira/browse/SPARK-23977). For Spark 2.4, the [HortonWorks backport](https://github.com/hortonworks-spark/cloud-integration/blob/master/spark-cloud-integration/src/main/site/markdown/index.md) is used from the [Hortonworks repo](https://mvnrepository.com/artifact/org.apache.spark/spark-hadoop-cloud_2.11/2.3.2.3.1.0.6-1).
