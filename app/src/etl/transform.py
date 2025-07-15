from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count
import os
import glob
from datetime import datetime

spark = SparkSession.builder.appName("BreweryPipeline").getOrCreate()

def transform_to_silver():
    files = glob.glob("data/bronze/*.json")
    if not files:
        raise FileNotFoundError("Nenhum arquivo encontrado na camada bronze.")

    df = spark.read.json(files[-1])
    df = df.select("id", "name", "brewery_type", "state").dropna()
    os.makedirs("data/silver", exist_ok=True)
    df.write.partitionBy("state").mode("overwrite").parquet("data/silver/breweries.parquet")

def aggregate_to_gold():
    df = spark.read.parquet("data/silver/breweries.parquet")
    agg_df = df.groupBy("state", "brewery_type").agg(count("id").alias("count"))
    os.makedirs("data/gold", exist_ok=True)
    agg_df.write.mode("overwrite").parquet("data/gold/breweries_aggregated.parquet")