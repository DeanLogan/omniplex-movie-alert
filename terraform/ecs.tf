resource "aws_ecs_task_definition" "scraper" {
  family                   = "movie-alerts"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "movie-alerts"
      image     = "${aws_ecr_repository.movie_alerts.repository_url}:latest"
      essential = true
      
      environment = [
        { name = "S3_BUCKET_NAME", value = aws_s3_bucket.movie_lists.bucket }
      ]
      
      secrets = [
        {
          name      = "APP_PASSWORD_GMAIL"
          valueFrom = aws_ssm_parameter.gmail_app_password.arn
        },
        {
          name      = "ERROR_EMAIL"
          valueFrom = aws_ssm_parameter.error_email.arn
        },
        {
          name      = "EMAIL_GMAIL"
          valueFrom = aws_ssm_parameter.sender_email.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.scraper.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
