locals {
  lambda_name = "movie-alerts"
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "movie-alerts-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_execution_policy" {
  name = "movie-alerts-lambda-execution"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "kms:Decrypt"
        ]
        Resource = [
          aws_ssm_parameter.gmail_app_password.arn,
          aws_ssm_parameter.error_email.arn,
          aws_ssm_parameter.sender_email.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.movie_lists.arn,
          "${aws_s3_bucket.movie_lists.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_function" "scraper" {
  function_name = local.lambda_name
  role          = aws_iam_role.lambda_execution_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.movie_alerts.repository_url}:latest"
  timeout       = 900
  memory_size   = 512

  environment {
    variables = {
      S3_BUCKET_NAME           = aws_s3_bucket.movie_lists.bucket
      APP_PASSWORD_GMAIL_PARAM = aws_ssm_parameter.gmail_app_password.name
      ERROR_EMAIL_PARAM        = aws_ssm_parameter.error_email.name
      EMAIL_GMAIL_PARAM        = aws_ssm_parameter.sender_email.name
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_execution_policy,
    aws_cloudwatch_log_group.scraper
  ]
}
