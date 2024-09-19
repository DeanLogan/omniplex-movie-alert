import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

load_dotenv()

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('S3_ENDPOINT_URL', 'https://s3.eu-north-1.amazonaws.com'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'eu-north-1')
)

def add_file(dir_local_file, filename):
    s3.upload_file(dir_local_file, 'movie-lists', filename)

def check_files_in_bucket():
    response = s3.list_objects(Bucket='movie-lists')
    print('Files in bucket:')
    for obj in response.get('Contents', []):
        print(f" - {obj['Key']}")

def get_file_from_bucket(filename):
    s3 = boto3.client('s3')
    temp_file_path = os.path.join('tmp', filename)
    
    try:
        s3.download_file('movie-lists', filename, temp_file_path)
    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        return None
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
        return None
    except ClientError as e:
        if e.response['Error']['Code'] == '403':
            print("Error: Access forbidden. Check your IAM permissions and bucket policy.")
        else:
            print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    return temp_file_path

def delete_file_from_bucket(filename):
    s3.delete_object(Bucket='movie-lists', Key=filename)

def delete_all_files_in_bucket():
    response = s3.list_objects(Bucket='movie-lists')
    for obj in response.get('Contents', []):
        s3.delete_object(Bucket='movie-lists', Key=obj['Key'])

def create_bucket():
    s3.create_bucket(Bucket='movie-lists')

if __name__ == "__main__":
    add_file("tmp/carrickfergus.txt")
    add_file("tmp/antrim.txt")
    check_files_in_bucket()