# Patient Readmission Risk Predictor — Complete Execution Steps

## Project Overview
End-to-end AWS Big Data pipeline to predict 30-day hospital readmissions
using PySpark ETL, Random Forest ML, and SQL analytics.

## Architecture
```
CSV Upload → S3 → Lambda (auto trigger) → AWS Glue (PySpark ETL)
→ S3 (Parquet) → EC2 (ML Model) → S3 (Model) → Athena (SQL Analysis)
```

## AWS Services Used
| Service | Purpose |
|---|---|
| Amazon S3 | Raw data + processed output storage |
| AWS Lambda | Auto-trigger Glue ETL on CSV upload |
| AWS Glue | PySpark ETL — clean and transform data |
| Amazon EC2 (t2.micro) | Train Random Forest ML model |
| Amazon Athena | SQL analysis on processed Parquet data |

## Dataset
- Name: Diabetes 130-US Hospitals (1999–2008)
- Source: https://www.kaggle.com/datasets/brandao/diabetes
- Size: 99,492 patient records, 50 features
- Target: Predict 30-day hospital readmission (binary classification)

---

# PHASE 1 — AWS Account Setup

## Step 1 — Create AWS Account
1. Go to aws.amazon.com
2. Click **Create an AWS Account** (top right)
3. Enter email address and account name: `readmission-project`
4. Enter personal details and debit/credit card (₹2 verification, refunded)
5. Choose **Basic Support (Free)** — do NOT select any paid plan
6. Verify OTP → account activates in 5–10 minutes

## Step 2 — Set Region to Mumbai
1. Log in to AWS Console
2. Top-right corner → click region dropdown
3. Select **Asia Pacific (Mumbai) — ap-south-1**
4. Keep this region for ALL services throughout the project

## Step 3 — Create IAM User
1. Search `IAM` in top search bar → click IAM
2. Left sidebar → **Users** → **Create user**
3. Username: `readmission-admin`
4. Tick **Provide user access to AWS Console**
5. Select **I want to create an IAM user**
6. Set a custom password → untick "must reset password"
7. Click Next → **Attach policies directly**
8. Search and tick each of these policies:
   - AmazonS3FullAccess
   - AWSGlueConsoleFullAccess
   - AWSLambda_FullAccess
   - AmazonAthenaFullAccess
   - AmazonEC2FullAccess
9. Click **Create user** → download the CSV file
10. Log out of root account → use IAM login URL from CSV for all future logins

---

# PHASE 2 — S3 Buckets Setup

## Step 4 — Create Raw Data Bucket
1. Search `S3` in top bar → click S3
2. Click **Create bucket**
3. Bucket name: `readmission-raw-vaishali`
4. Region: ap-south-1
5. Block all public access: keep all 4 boxes ticked
6. Versioning: **Enable**
7. Click **Create bucket**

## Step 5 — Create Processed Data Bucket
1. Click **Create bucket**
2. Bucket name: `readmission-processed-vaishali`
3. Region: ap-south-1
4. Keep all defaults → click **Create bucket**
5. Click into the bucket → **Create folder** → name: `output` → Create folder
6. Create another folder → name: `scripts` → Create folder
7. Create another folder → name: `athena-results` → Create folder

## Step 6 — Create ML Results Bucket
1. Click **Create bucket**
2. Bucket name: `readmission-ml-results-vaishali`
3. Region: ap-south-1
4. Keep all defaults → click **Create bucket**
5. Inside bucket → **Create folder** → name: `model` → Create folder

## Step 7 — Upload Dataset to S3
1. Go to `readmission-raw-vaishali` bucket
2. Click **Upload** → **Add files**
3. Select `diabetic_data.csv` downloaded from Kaggle
4. Click **Upload** → wait for completion
5. Confirm file is listed inside the bucket

## Step 8 — Upload Glue Script to S3
1. Go to `readmission-processed-vaishali` bucket → open `scripts` folder
2. Click **Upload** → **Add files**
3. Select `etl_job.py` from your laptop
4. Click **Upload**
5. After upload click the file → copy its S3 URI:
   `s3://readmission-processed-vaishali/scripts/`

---

# PHASE 3 — Lambda Function Setup

## Step 9 — Create Lambda Function
1. Search `Lambda` in top bar → click Lambda
2. Click **Create function**
3. Select **Author from scratch**
4. Function name: `trigger-glue-etl`
5. Runtime: **Python 3.12**
6. Architecture: x86_64
7. Click **Create function**

## Step 10 — Add IAM Permission to Lambda
1. Inside Lambda function → click **Configuration** tab
2. Click **Permissions**
3. Click the **Role name** link (opens IAM in new tab)
4. Click **Add permissions** → **Attach policies**
5. Search `AWSGlueConsoleFullAccess` → tick → click **Add permissions**
6. Repeat for `AmazonS3FullAccess`

## Step 11 — Paste Lambda Code
1. Back on Lambda function page → click **Code** tab
2. Click on `lambda_function.py` in the editor
3. Select all and delete existing code
4. Paste the following code:

```python
import boto3

def lambda_handler(event, context):
    glue = boto3.client('glue', region_name='ap-south-1')
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    response = glue.start_job_run(
        JobName='readmission-etl-job',
        Arguments={
            '--input_path': f's3://{bucket}/{key}',
            '--output_path': 's3://readmission-processed-vaishali/output/'
        }
    )
    print(f"Glue job started: {response['JobRunId']}")
    return {'statusCode': 200, 'body': 'Glue job triggered'}
```

5. Click **Deploy** (orange button)
6. Confirm "Changes deployed" message appears

## Step 12 — Add S3 Trigger to Lambda
1. On Lambda function page → click **+ Add trigger**
2. Source: select **S3**
3. Bucket: select `readmission-raw-vaishali`
4. Event types: select **PUT**
5. Suffix: `.csv`
6. Tick the acknowledgement checkbox
7. Click **Add**

---

# PHASE 4 — AWS Glue ETL Job

## Step 13 — Create IAM Role for Glue
1. Search `IAM` → **Roles** → **Create role**
2. Trusted entity type: **AWS service**
3. Use case: scroll down → select **Glue** → click Next
4. Attach these policies:
   - AmazonS3FullAccess
   - AWSGlueServiceRole
5. Click Next → Role name: `AWSGlueServiceRole-readmission`
6. Click **Create role**

## Step 14 — Create Glue ETL Job
1. Search `Glue` → click AWS Glue
2. Left sidebar → **ETL Jobs**
3. Click **Visual ETL**
4. On next page click **Script editor**
5. Engine: **Spark**
6. Select **Upload and edit an existing script**
7. Choose your `etl_job.py` file → click **Create**

## Step 15 — Configure Glue Job Settings
1. Click **Job details** tab
2. Fill in:
   - Name: `readmission-etl-job`
   - IAM Role: `AWSGlueServiceRole-readmission`
   - Type: Spark
   - Glue version: Glue 4.0
   - Language: Python 3
   - Worker type: G.1X
   - Number of workers: 2
   - Job timeout: 10 minutes
   - Max retries: 0
3. Script path: `s3://readmission-processed-vaishali/scripts/`
4. Script filename: `etl_job.py`
5. Click **Save** (top right)

## Step 16 — Run Glue Job
1. Click **Run** button (top right)
2. Click **Run job** in the dialog
3. Go to **Runs** tab
4. Wait 3–5 minutes for status to change to **Succeeded**
5. Verify output: Go to S3 → `readmission-processed-vaishali` → `output` folder
6. Confirm `.parquet` files are present

### Glue ETL Script (etl_job.py)
```python
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
```

---

# PHASE 5 — EC2 ML Model Training

## Step 17 — Launch EC2 Instance
1. Search `EC2` → click **Launch instance**
2. Fill in:
   - Name: `readmission-ml-server`
   - AMI: **Amazon Linux 2023 AMI** (Free tier eligible)
   - Instance type: **t2.micro** (Free tier eligible)
3. Key pair → **Create new key pair**:
   - Name: `readmission-key`
   - Type: RSA
   - Format: .pem
   - Click **Create key pair** (file downloads automatically — save it safely)
4. Network settings: Allow SSH traffic from → **My IP**
5. Storage: 8 GB gp2 (default)
6. Click **Launch instance** → wait 2 minutes

## Step 18 — Attach S3 Role to EC2
1. Search `IAM` → **Roles** → **Create role**
2. AWS service → **EC2** → Next
3. Attach `AmazonS3FullAccess` → Next
4. Role name: `EC2-S3-ReadmissionRole` → **Create role**
5. Go to EC2 → select your instance
6. Click **Actions** → **Security** → **Modify IAM role**
7. Select `EC2-S3-ReadmissionRole` → **Update IAM role**

## Step 19 — Connect to EC2
1. EC2 → select your instance → click **Connect** (top right)
2. Choose **EC2 Instance Connect** tab
3. Click **Connect**
4. Black browser terminal opens — you are now inside the server

## Step 20 — Install Python Packages
Run these commands one by one in the EC2 terminal:
```bash
sudo yum update -y
sudo yum install python3-pip -y
pip3 install pandas scikit-learn boto3 pyarrow joblib
```

## Step 21 — Create and Run Training Script
1. In EC2 terminal type: `nano train_model.py`
2. Paste the train_model.py code
3. Press `Ctrl + X` → `Y` → `Enter` to save
4. Run the script:
```bash
python3 train_model.py
```
5. Wait 2–3 minutes for output:
```
Loaded 99492 rows
--- Classification Report ---
ROC-AUC Score: 0.72+
Model saved to S3 successfully!
```

## Step 22 — Stop EC2 Instance (Important!)
1. Go to EC2 → select your instance
2. Click **Instance state** → **Stop instance**
3. Always stop EC2 when not in use to avoid charges

---

# PHASE 6 — Amazon Athena SQL Analysis

## Step 23 — Configure Athena
1. Search `Athena` → click Amazon Athena
2. Click **Settings** tab
3. Query result location: `s3://readmission-processed-vaishali/athena-results/`
4. Click **Save**

## Step 24 — Create Database
Go to **Query editor** → paste and click **Run**:
```sql
CREATE DATABASE readmission_db;
```

## Step 25 — Create Table
Change Database dropdown to `readmission_db` → paste and run:
```sql
CREATE EXTERNAL TABLE readmission_db.processed_data (
  age_numeric       INT,
  time_in_hospital  INT,
  num_procedures    INT,
  num_medications   INT,
  number_diagnoses  INT,
  readmitted_30     INT
)
STORED AS PARQUET
LOCATION 's3://readmission-processed-vaishali/output/'
TBLPROPERTIES ('parquet.compress'='SNAPPY');
```

## Step 26 — Run Analysis Queries

### Query 1: Verify Data
```sql
SELECT * FROM readmission_db.processed_data LIMIT 10;
```

### Query 2: Overall Readmission Rate
```sql
SELECT
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted_within_30_days,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 2) AS readmission_rate_pct
FROM readmission_db.processed_data;
```

### Query 3: Readmission Rate by Age Group
```sql
SELECT
  age_numeric / 10 * 10 AS age_decade,
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 1) AS readmit_pct
FROM readmission_db.processed_data
GROUP BY 1
ORDER BY 1;
```

### Query 4: Average Stay for Readmitted vs Not Readmitted
```sql
SELECT
  readmitted_30,
  ROUND(AVG(time_in_hospital), 2) AS avg_stay_days,
  ROUND(AVG(num_medications), 2) AS avg_medications,
  ROUND(AVG(number_diagnoses), 2) AS avg_diagnoses,
  COUNT(*) AS patient_count
FROM readmission_db.processed_data
GROUP BY 1;
```

### Query 5: High Risk Patients
```sql
SELECT *
FROM readmission_db.processed_data
WHERE time_in_hospital > 7
  AND number_diagnoses > 7
  AND readmitted_30 = 1
LIMIT 20;
```

### Query 6: Readmission by Number of Medications
```sql
SELECT
  num_medications,
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 1) AS readmit_pct
FROM readmission_db.processed_data
GROUP BY 1
ORDER BY readmit_pct DESC
LIMIT 10;
```

### Query 7: Readmission by Number of Diagnoses
```sql
SELECT
  number_diagnoses,
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 1) AS readmit_pct
FROM readmission_db.processed_data
GROUP BY 1
ORDER BY number_diagnoses;
```

### Query 8: Readmission by Hospital Stay Duration
```sql
SELECT
  time_in_hospital,
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 1) AS readmit_pct
FROM readmission_db.processed_data
GROUP BY 1
ORDER BY time_in_hospital;
```

---

# PHASE 7 — End-to-End Pipeline Test

## Step 27 — Test Auto Trigger
1. Go to S3 → `readmission-raw-vaishali`
2. Click **Upload** → upload `diabetic_data.csv` again
3. Go to **Lambda** → `trigger-glue-etl` → **Monitor** tab
4. Click **View CloudWatch logs**
5. Confirm log entry shows: `Glue job started: jr_XXXXXXXX`
6. Go to **Glue** → **ETL Jobs** → `readmission-etl-job` → **Runs** tab
7. Confirm new run started automatically and shows **Succeeded**

## Step 28 — Set Up Billing Alert
1. Click account name (top right) → **Billing and Cost Management**
2. Left sidebar → **Budgets** → **Create budget**
3. Select **Use a template** → **Zero spend budget**
4. Enter your email → **Create budget**

---

# Project Results

| Metric | Value |
|---|---|
| Dataset size | 99,492 patients |
| ML Algorithm | Random Forest Classifier |
| ROC-AUC Score | 0.72+ |
| Overall readmission rate | ~11% |
| Top risk factor | number_diagnoses |
| Total AWS cost | ~₹5 |

---

# Key Interview Questions

**Q: Why Parquet instead of CSV?**
Parquet is columnar — 3-5x smaller than CSV. Athena charges per data
scanned so Parquet reduces query cost significantly.

**Q: Why is 88% accuracy misleading?**
Dataset has only 11% readmitted patients. A model predicting "no
readmission" every time gets 89% accuracy without learning anything.
That is why ROC-AUC and precision/recall are better metrics.

**Q: Why Lambda instead of scheduled Glue job?**
Lambda makes the pipeline event-driven — ETL starts the moment new
data arrives. No wasted compute when there is no new data.

**Q: How would you scale this to production?**
Replace EC2 with SageMaker for managed ML. Add EventBridge for
scheduling. Use Redshift Spectrum for larger datasets.

---

# Author
**Vaishali Kawadapure**
PG Diploma in Big Data Analytics — CDAC Chennai

