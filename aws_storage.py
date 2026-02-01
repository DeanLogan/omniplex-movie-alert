import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

AWS_SERVICE_S3 = 's3'
BUCKET_NAME = 'movie-lists'

HTTP_FORBIDDEN = '403'
TMP_DIRECTORY = 'tmp'

ENV_S3_ENDPOINT_URL = 'S3_ENDPOINT_URL'
ENV_AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
ENV_AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
ENV_AWS_REGION = 'AWS_REGION'

S3_CONTENTS_KEY = 'Contents'
S3_KEY_FIELD = 'Key'
S3_ERROR_CODE = 'Error'
S3_CODE_FIELD = 'Code'

ERROR_NO_CREDENTIALS = "Error: AWS credentials not found."
ERROR_PARTIAL_CREDENTIALS = "Error: Incomplete AWS credentials."
ERROR_ACCESS_FORBIDDEN = "Error: Access forbidden. Check your IAM permissions and bucket policy."

load_dotenv()

s3 = boto3.client(
    AWS_SERVICE_S3,
    endpoint_url=os.getenv(ENV_S3_ENDPOINT_URL),
    aws_access_key_id=os.getenv(ENV_AWS_ACCESS_KEY_ID),
    aws_secret_access_key=os.getenv(ENV_AWS_SECRET_ACCESS_KEY),
    region_name=os.getenv(ENV_AWS_REGION)
)

def add_file(dir_local_file, filename):
    s3.upload_file(dir_local_file, BUCKET_NAME, filename)

def check_files_in_bucket():
    response = s3.list_objects(Bucket=BUCKET_NAME)
    print('Files in bucket:')
    for obj in response.get(S3_CONTENTS_KEY, []):
        print(f" - {obj[S3_KEY_FIELD]}")

def get_file_from_bucket(filename):
    s3 = boto3.client(AWS_SERVICE_S3, region_name=os.getenv(ENV_AWS_REGION)
    temp_file_path = os.path.join(TMP_DIRECTORY, filename)
    
    try:
        s3.download_file(BUCKET_NAME, filename, temp_file_path)
    except NoCredentialsError:
        print(ERROR_NO_CREDENTIALS)
        return None
    except PartialCredentialsError:
        print(ERROR_PARTIAL_CREDENTIALS)
        return None
    except ClientError as e:
        if e.response[S3_ERROR_CODE][S3_CODE_FIELD] == HTTP_FORBIDDEN:
            print(ERROR_ACCESS_FORBIDDEN)
        else:
            print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    return temp_file_path

def delete_file_from_bucket(filename):
    s3.delete_object(Bucket=BUCKET_NAME, Key=filename)

def delete_all_files_in_bucket():
    response = s3.list_objects(Bucket=BUCKET_NAME)
    for obj in response.get(S3_CONTENTS_KEY, []):
        s3.delete_object(Bucket=BUCKET_NAME, Key=obj[S3_KEY_FIELD])

def create_bucket():
    s3.create_bucket(Bucket=BUCKET_NAME)

if __name__ == "__main__":
    get_file_from_bucket("antrim.txt")
    get_file_from_bucket("carrickfergus.txt")
    get_file_from_bucket("larne.txt")
    get_file_from_bucket("email_list.json")