def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Success, this ran'
    }

if __name__ == '__main__':
    lambda_handler(None, None)