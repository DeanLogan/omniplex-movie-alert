import boto3
import json
import os
import shutil



# Save current directory
original_dir = os.getcwd()

# Change directory to 'package'
os.chdir('package')

# Create functions.zip with contents of package folder
shutil.make_archive("function", "zip", ".")

# Move the zip file to the original directory
shutil.move("function.zip", original_dir)

# Change back to original directory
os.chdir(original_dir)

# Configure Boto3 to use LocalStack
localstack_endpoint_url = 'http://localhost:4566'
s3 = boto3.client(
    's3',
    endpoint_url=localstack_endpoint_url,
    aws_access_key_id='dummyAccessKeyId',
    aws_secret_access_key='dummySecretAccessKey',
    region_name='us-east-1'
)

iam = boto3.client(
    'iam',
    endpoint_url=localstack_endpoint_url,
    aws_access_key_id='dummyAccessKeyId',
    aws_secret_access_key='dummySecretAccessKey',
    region_name='us-east-1'
)

lambda_client = boto3.client(
    'lambda',
    endpoint_url=localstack_endpoint_url,
    aws_access_key_id='dummyAccessKeyId',
    aws_secret_access_key='dummySecretAccessKey',
    region_name='us-east-1'
)

# Step 1: Create S3 bucket
bucket_name = 'my-lambda-bucket'
s3.create_bucket(Bucket=bucket_name)
print(f'Created bucket {bucket_name}')

# Step 2: Upload the deployment package
function_zip = 'function.zip'
s3.upload_file(function_zip, bucket_name, function_zip)
print(f'Uploaded {function_zip} to {bucket_name}')

# Step 3: Create IAM role
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

role_name = 'lambda-ex'
try:
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy)
    )
    print(f'Created IAM role {role_name}')
except iam.exceptions.EntityAlreadyExistsException:
    print(f'Role {role_name} already exists')

try:
    response = lambda_client.delete_function(FunctionName='my-lambda-function')
    print("Lambda function deleted successfully:", response)
except lambda_client.exceptions.ResourceNotFoundException:
    print("Lambda function does not exist")
    
# Step 4: Create Lambda function
try:
    with open("function.zip", 'rb') as f:
            zip_file_contents = f.read()

    lambda_client.create_function(
        FunctionName='my-lambda-function',
        Runtime='python3.12',
        Role=f'arn:aws:iam::000000000000:role/{role_name}',
        Handler='movie_alerts.lambda_handler',
        Code={'ZipFile': zip_file_contents},
        Timeout=900,
    )
    print('Created Lambda function my-lambda-function')
except lambda_client.exceptions.ResourceConflictException:
    print('Function already exists, updating code')
    lambda_client.update_function_code(
        FunctionName='my-lambda-function',
        S3Bucket=bucket_name,
        S3Key=function_zip
    )
    print('Updated Lambda function my-lambda-function')