import boto3
import os
import json

with open(os.path.join("secrets", "s3_secrets.json"), 'rb') as secrets_file:
    secrets_json = json.load(secrets_file)

S3_KEY = secrets_json.get("S3_KEY")
S3_SECRET_ACCESS_KEY = secrets_json.get("S3_SECRET_ACCESS_KEY")
S3_BUCKET = 'data-hunter-results'
resource = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                        region_name='eu-west-2')


def upload_file(file, bucket_path, bucket=S3_BUCKET):
    """Upload a file to a bucket."""
    #  Bucket path should be somedir/name_of_file.ext
    try:
        if isinstance(file, str):
            resource.upload_file(file, bucket, bucket_path)
        else:
            resource.upload_fileobj(file, bucket, bucket_path)
    except:
        raise ChildProcessError('Something broke, Cap\'n')
