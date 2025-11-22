import os
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")

s3 = boto3.client('s3', region_name=AWS_REGION)
dynamo = boto3.resource('dynamodb', region_name=AWS_REGION)

def upload_file_to_s3(local_path, s3_key):
    if not S3_BUCKET:
        raise Exception("S3_BUCKET not set")
    try:
        s3.upload_file(local_path, S3_BUCKET, s3_key)
        return f"s3://{S3_BUCKET}/{s3_key}"
    except ClientError as e:
        raise

def write_metadata_dynamo(table_name, item):
    table = dynamo.Table(table_name)
    table.put_item(Item=item)
