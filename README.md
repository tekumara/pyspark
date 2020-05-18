# Spark with S3A

This distribution of Spark bundles [hadoop-aws 3.1](https://hadoop.apache.org/docs/r3.1.0/hadoop-aws/tools/hadoop-aws/index.html) which contains optimised committers
and the [HortonWorks backport](https://github.com/hortonworks-spark/cloud-integration/blob/master/spark-cloud-integration/src/main/site/markdown/index.md) to use the committers with Spark 2.4.x.

## Install

```
pip install https://github.com/tekumara/spark/releases/download/v.2.4.5-cloud/pyspark-2.4.5.tar.gz
```

See [test_s3a.py](https://github.com/tekumara/spark/blob/dee3073ab93afa8b5807c09f852a415d7ec7bb4c/python/test_dist/test_s3a.py#L43) for an example of using the staging committers

## Rationale

Common practice is to use hadoop-aws 2.7.3 as follows: 

```
pyspark --packages "org.apache.hadoop:hadoop-aws:2.7.3" --driver-java-options "-Dspark.hadoop.fs.s3.impl=org.apache.hadoop.fs.s3a.S3AFileSystem"
```
However later versions of hadoop-aws cannot be used this way without errors. 

Later versions of hadoop-aws contain the following new features:
* [2.8 release line](http://hadoop.apache.org/docs/r2.8.0/index.html) contains S3A improvements to 
support any AWSCredentialsProvider
* [2.9 release line](http://hadoop.apache.org/docs/r2.9.0/index.html) contains 
[S3Guard](http://hadoop.apache.org/docs/r2.9.0/hadoop-aws/tools/hadoop-aws/s3guard.html) which provides 
consistency and metadata caching for S3A via a backing DynamoDB metadata store.
* [3.1 release line](http://hadoop.apache.org/docs/r3.1.0/index.html) incorporates HADOOP-13786 which 
contains optimised job committers including the Netflix staging committers (Directory and Partitioned) 
and the Magic committers. See 
[committers](https://github.com/apache/hadoop/blob/branch-3.1/hadoop-tools/hadoop-aws/src/site/markdown/tools/hadoop-aws/committers.md) and [committer architecture](https://github.com/apache/hadoop/blob/trunk/hadoop-tools/hadoop-aws/src/site/markdown/tools/hadoop-aws/committer_architecture.md).

To take advantage of the 3.1 release line committers in Spark you also need the binding classes introduced into
Spark 3.0.0 by [SPARK-23977](https://issues.apache.org/jira/browse/SPARK-23977). For Spark 2.4, a backport is
available from the [Hortonworks repo](https://mvnrepository.com/artifact/org.apache.spark/spark-hadoop-cloud_2.11/2.3.2.3.1.0.6-1).

This distribution [builds a Spark 2.4.x distribution](https://github.com/tekumara/spark/blob/dee3073ab93afa8b5807c09f852a415d7ec7bb4c/.github/workflows/spark-cloud.yml#L60) from source 
with Hadoop 3.1 and the additional [Hortonworks backport dependency](https://github.com/tekumara/spark/blob/dee3073ab93afa8b5807c09f852a415d7ec7bb4c/hadoop-cloud/pom.xml#L248).
