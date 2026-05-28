--CREATE DATABSE
CREATE DATABASE readmission_db;

--CREATE TABLE
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

--Verify Table (run this first to confirm data loaded)
SELECT * FROM readmission_db.processed_data
LIMIT 10;

--Analysis Query 1: Overall Readmission Rate
SELECT
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted_within_30_days,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 2) AS readmission_rate_pct
FROM readmission_db.processed_data;

--Analysis Query 2: Readmission Rate by Age Group
SELECT
  age_numeric / 10 * 10 AS age_decade,
  COUNT(*) AS total_patients,
  SUM(readmitted_30) AS readmitted,
  ROUND(100.0 * SUM(readmitted_30) / COUNT(*), 1) AS readmit_pct
FROM readmission_db.processed_data
GROUP BY 1
ORDER BY 1;

--Analysis Query 3: Average Stay for Readmitted vs Not
SELECT
  readmitted_30,
  ROUND(AVG(time_in_hospital), 2) AS avg_stay_days,
  ROUND(AVG(num_medications), 2) AS avg_medications,
  ROUND(AVG(number_diagnoses), 2) AS avg_diagnoses,
  COUNT(*) AS patient_count
FROM readmission_db.processed_data
GROUP BY 1;

--Analysis Query 4: High Risk Patients
SELECT *
FROM readmission_db.processed_data
WHERE time_in_hospital > 7
  AND number_diagnoses > 7
  AND readmitted_30 = 1
LIMIT 20;



