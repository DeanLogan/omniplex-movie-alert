import os
import boto3

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
    temp_file_path = os.path.join('tmp', filename)
    s3.download_file('movie-lists', filename, temp_file_path)
    return temp_file_path

def delete_file_from_bucket(filename):
    s3.delete_object(Bucket='movie-lists', Key=filename)

def delete_all_files_in_bucket():
    response = s3.list_objects(Bucket='movie-lists')
    for obj in response.get('Contents', []):
        s3.delete_object(Bucket='movie-lists', Key=obj['Key'])

def create_bucket():
    s3.create_bucket(Bucket='movie-lists')

# create_bucket()
# add_file('geckodriver', 'geckodriver')
# check_files_in_bucket()