import os
import boto3
from dotenv import load_dotenv
from functools import lru_cache
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

AWS_SERVICE_S3 = 's3'
AWS_SERVICE_SSM = 'ssm'
BUCKET_NAME = 'movie-lists'

HTTP_FORBIDDEN = '403'
TMP_DIRECTORY = '/tmp'

SSM_STORE_PATH = '/movie-alerts/prod/'

ENV_S3_ENDPOINT_URL = 'S3_ENDPOINT_URL'
ENV_AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
ENV_AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
ENV_AWS_REGION = 'AWS_REGION'

S3_CONTENTS_KEY = 'Contents'
S3_KEY_FIELD = 'Key'
S3_ERROR_CODE = 'Error'
S3_CODE_FIELD = 'Code'
S3_BUCKET_NAME = 'S3_BUCKET_NAME'

ERROR_NO_CREDENTIALS = "Error: AWS credentials not found."
ERROR_PARTIAL_CREDENTIALS = "Error: Incomplete AWS credentials."
ERROR_ACCESS_FORBIDDEN = "Error: Access forbidden. Check your IAM permissions and bucket policy."

SSM_SECRET_MAP = {
    'SENDER_EMAIL': SSM_STORE_PATH+'sender_email',
    'APP_PASSWORD_GMAIL': SSM_STORE_PATH+'gmail_app_password',
    'ERROR_EMAIL': SSM_STORE_PATH+'error_email',
}

def load_env():
    load_dotenv()

    missing = {
        env_var: ssm_path
        for env_var, ssm_path in SSM_SECRET_MAP.items()
        if not os.getenv(env_var)
    }
    if not missing:
        return

    ssm = boto3.client(AWS_SERVICE_SSM)
    response = ssm.get_parameters(Names=list(missing.values()), WithDecryption=True)

    path_to_env_var = {ssm_path: env_var for env_var, ssm_path in missing.items()}
    for param in response['Parameters']:
        os.environ[path_to_env_var[param['Name']]] = param['Value']

    if response.get('InvalidParameters'):
        raise RuntimeError(f"Missing SSM parameters: {response['InvalidParameters']}")

@lru_cache(maxsize=1)
def create_s3_client():
    return boto3.client(AWS_SERVICE_S3)

def add_file(dir_local_file, filename):
    create_s3_client().upload_file(dir_local_file, os.getenv(S3_BUCKET_NAME, BUCKET_NAME), filename)

def check_files_in_bucket():
    response = create_s3_client().list_objects(Bucket=os.getenv(S3_BUCKET_NAME, BUCKET_NAME))
    print('Files in bucket:')
    for obj in response.get(S3_CONTENTS_KEY, []):
        print(f" - {obj[S3_KEY_FIELD]}")

def get_file_from_bucket(filename):
    os.makedirs(TMP_DIRECTORY, exist_ok=True)
    temp_file_path = os.path.join(TMP_DIRECTORY, filename)
    
    try:
        create_s3_client().download_file(os.getenv(S3_BUCKET_NAME, BUCKET_NAME), filename, temp_file_path)
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
    create_s3_client().delete_object(Bucket=os.getenv(S3_BUCKET_NAME, BUCKET_NAME), Key=filename)

def delete_all_files_in_bucket():
    response = create_s3_client().list_objects(Bucket=os.getenv(S3_BUCKET_NAME, BUCKET_NAME))
    for obj in response.get(S3_CONTENTS_KEY, []):
        create_s3_client().delete_object(Bucket=os.getenv(S3_BUCKET_NAME, BUCKET_NAME), Key=obj[S3_KEY_FIELD])

def create_bucket():
    create_s3_client().create_bucket(Bucket=BUCKET_NAME)

if __name__ == "__main__":
    load_env()
    delete_file_from_bucket("carrickfergus.txt")