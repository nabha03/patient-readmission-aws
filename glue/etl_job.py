from pyspark.context import SparkContext
from awsglue.context import GlueContext
import pyspark.sql.functions as F

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

input_path  = 's3://readmission-raw-vaishali/diabetic_data.csv'
output_path = 's3://readmission-processed-vaishali/output/'

df = spark.read.csv(input_path, header=True, inferSchema=True)
df = df.dropna(subset=['age', 'readmitted'])
df = df.withColumn('readmitted_30',
    F.when(F.col('readmitted') == '<30', 1).otherwise(0))
df = df.withColumn('age_numeric',
    F.regexp_extract(F.col('age'), r'(\d+)', 1).cast('int'))

feature_cols = ['age_numeric', 'time_in_hospital', 'num_procedures',
                'num_medications', 'number_diagnoses', 'readmitted_30']

df.select(feature_cols).write.mode('overwrite').parquet(output_path)
print("ETL complete!")
