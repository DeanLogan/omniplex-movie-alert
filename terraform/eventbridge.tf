resource "aws_iam_role" "scheduler_lambda" {
  name = "movie-alerts-scheduler-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_lambda" {
  name = "movie-alerts-scheduler-lambda"
  role = aws_iam_role.scheduler_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["lambda:InvokeFunction"]
      Resource = aws_lambda_function.scraper.arn
    }]
  })
}

resource "aws_scheduler_schedule" "scraper_schedule" {
  name                         = "movie-alerts-schedule"
  description                  = "Run movie alerts every day at 10am UK time"
  schedule_expression          = "cron(0 10 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.scraper.arn
    role_arn = aws_iam_role.scheduler_lambda.arn
  }
}

resource "aws_lambda_permission" "allow_scheduler" {
  statement_id  = "AllowExecutionFromEventBridgeScheduler"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scraper.function_name
  principal     = "scheduler.amazonaws.com"
  source_arn    = aws_scheduler_schedule.scraper_schedule.arn
}
