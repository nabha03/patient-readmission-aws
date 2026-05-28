from pyspark.context import SparkContext
from awsglue.context import GlueContext
import pyspark.sql.functions as F

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

input_path  = 's3://readmission-raw-vaishali/diabetic_data.csv'
output_path = 's3://readmission-processed-vaishali/output/'

df = spark.read.csv(input_path, header=True, inferSchema=True)

# Remove test/hospice/expired discharge patients
# (they cannot be readmitted so they skew the model)
df = df.filter(~F.col('discharge_disposition_id').isin(['11','13','14','19','20','21']))

# Target column
df = df.withColumn('readmitted_30',
    F.when(F.col('readmitted') == '<30', 1).otherwise(0))

# Age to number
df = df.withColumn('age_numeric',
    F.regexp_extract(F.col('age'), r'(\d+)', 1).cast('int'))

# Cast important columns
df = df.withColumn('discharge_id',
    F.col('discharge_disposition_id').cast('int'))
df = df.withColumn('admission_type',
    F.col('admission_type_id').cast('int'))
df = df.withColumn('admission_source',
    F.col('admission_source_id').cast('int'))
df = df.withColumn('num_emergency',
    F.col('number_emergency').cast('int'))
df = df.withColumn('num_inpatient',
    F.col('number_inpatient').cast('int'))
df = df.withColumn('num_outpatient',
    F.col('number_outpatient').cast('int'))

# Select all important features
feature_cols = [
    'age_numeric',
    'time_in_hospital',
    'num_procedures',
    'num_medications',
    'number_diagnoses',
    'discharge_id',
    'admission_type',
    'admission_source',
    'num_emergency',
    'num_inpatient',
    'num_outpatient',
    'readmitted_30'
]

df.select(feature_cols).dropna().write.mode('overwrite').parquet(output_path)
print("ETL complete!")
