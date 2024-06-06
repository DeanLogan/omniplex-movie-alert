import os
import boto3

# Configure Boto3 to use LocalStack
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='dummyAccessKeyId',
    aws_secret_access_key='dummySecretAccessKey',
    region_name='us-east-1'
)

def add_file(dir_local_file, filename):
    s3.upload_file(dir_local_file, 'movie-lists', filename)

def check_files_in_bucket():
    response = s3.list_objects(Bucket='movie-lists')
    print('Files in bucket:')
    for obj in response.get('Contents', []):
        print(f" - {obj['Key']}")

def get_file_from_bucket(filename):
    temp_file_path = os.path.join('tmp', filename)
    s3.download_file('movie-lists', filename, temp_file_path)
    return temp_file_path

def delete_file_from_bucket(filename):
    s3.delete_object(Bucket='movie-lists', Key=filename)

def delete_all_files_in_bucket():
    response = s3.list_objects(Bucket='movie-lists')
    for obj in response.get('Contents', []):
        s3.delete_object(Bucket='movie-lists', Key=obj['Key'])

filepath = add_file('tmp/larne.txt', "larne.txt")