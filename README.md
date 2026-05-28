# patient-readmission-aws
End-to-end hospital readmission risk predictor using AWS
##  Problem Statement
Hospital readmission within 30 days costs hospitals crores of rupees 
and indicates poor patient care. This project builds a complete 
end-to-end AWS data pipeline to predict which patients are at high 
risk of readmission using historical hospital data.

##  Architecture
CSV Upload → S3 → Lambda → AWS Glue (PySpark ETL) → S3 (Parquet) → EC2 (ML Model) → S3 → Athena (SQL Analysis)


## 🛠️ AWS Services Used
| Service | Purpose |
|---|---|
| Amazon S3 | Raw data storage + processed output |
| AWS Lambda | Auto-trigger Glue ETL on CSV upload |
| AWS Glue | PySpark ETL — clean and transform data |
| Amazon EC2 | Train Random Forest ML model |
| Amazon Athena | SQL analysis on processed data |


## 📊 Dataset
- **Name:** Diabetes 130-US Hospitals (1999–2008)
- **Source:** Kaggle — kaggle.com/datasets/brandao/diabetes
- **Size:** 99,492 patient records, 50 features
- **Target:** Predict 30-day hospital readmission (binary)

## 🤖 ML Model
- **Algorithm:** Random Forest Classifier
- **ROC-AUC Score:** 0.72+
- **Handling class imbalance:** class_weight='balanced'
- **Top features:** number_diagnoses, num_medications, time_in_hospital

  ## 📁 Project Structure
patient-readmission-aws/
├── lambda/trigger_glue.py     # Lambda trigger function
├── glue/etl_job.py            # PySpark ETL script
├── ml/train_model.py          # ML training script
├── athena/queries.sql         # SQL analysis queries
└── README.md

## ⚙️ Pipeline Flow
1. Raw CSV uploaded to S3
2. Lambda automatically triggers Glue ETL job
3. Glue cleans data and writes Parquet files to S3
4. EC2 trains Random Forest model on processed data
5. Model saved back to S3
6. Athena queries results for business insights

## 💡 Key Learnings
- Built serverless event-driven pipeline using S3 + Lambda
- Used PySpark on AWS Glue for scalable ETL
- Handled class imbalance in healthcare ML data
- Used columnar Parquet format for cost-efficient Athena queries

  
## 👩‍💻 Author
Vaishali Kawadapure
PG Diploma in Big Data Analytics — CDAC Chennai
