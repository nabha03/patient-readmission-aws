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
