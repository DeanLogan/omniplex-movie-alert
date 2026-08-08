resource "aws_lambda_function" "scraper" {
  function_name = "movie-alerts"
  role          = aws_iam_role.lambda_execution_role.arn
  package_type  = "Zip"
  timeout       = 900
  memory_size   = 512
  runtime       = "python3.12"
  handler       = "main.lambda_handler"

  filename = "${path.module}/../lambda.zip"

  environment {
    variables = {
      S3_BUCKET_NAME           = aws_s3_bucket.movie_lists.bucket
      APP_PASSWORD_GMAIL_PARAM = aws_ssm_parameter.gmail_app_password.name
      ERROR_EMAIL_PARAM        = aws_ssm_parameter.error_email.name
      EMAIL_GMAIL_PARAM        = aws_ssm_parameter.sender_email.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_execution_policy
  ]
}
