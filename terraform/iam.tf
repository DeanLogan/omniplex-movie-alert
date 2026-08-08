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
