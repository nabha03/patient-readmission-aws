import pandas as pd
import boto3
import joblib
import io
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

s3 = boto3.client('s3', region_name='ap-south-1')
bucket = 'readmission-processed-vaishali'
prefix = 'output/'

# Load parquet files from S3
paginator = s3.get_paginator('list_objects_v2')
dfs = []
for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    for obj in page.get('Contents', []):
        if obj['Key'].endswith('.parquet'):
            data = s3.get_object(Bucket=bucket, Key=obj['Key'])
            dfs.append(pd.read_parquet(io.BytesIO(data['Body'].read())))

df = pd.concat(dfs, ignore_index=True)
print(f"Loaded {len(df)} rows")

# Features and target
X = df.drop('readmitted_30', axis=1).fillna(0)
y = df['readmitted_30']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Gradient Boosting — better for imbalanced healthcare data
model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    min_samples_split=50,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {round(auc, 3)}")

# Feature importance
print("\n--- Feature Importance ---")
for feat, imp in sorted(zip(X.columns, model.feature_importances_),
                        key=lambda x: -x[1]):
    print(f"  {feat}: {round(imp, 3)}")

# Save model to S3
joblib.dump(model, '/tmp/readmission_model.pkl')
s3.upload_file('/tmp/readmission_model.pkl',
               'readmission-ml-results-vaishali',
               'model/readmission_model.pkl')
print("\nModel saved to S3 successfully!")
