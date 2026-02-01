resource "aws_iam_role" "eventbridge_ecs" {
  name = "movie-alerts-eventbridge-ecs-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "events.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "eventbridge_ecs" {
  name = "movie-alerts-eventbridge-ecs"
  role = aws_iam_role.eventbridge_ecs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["ecs:RunTask"]
      Resource = aws_ecs_task_definition.scraper.arn
    }]
  })
}

resource "aws_cloudwatch_event_rule" "scraper_schedule" {
  name                = "movie-alerts-schedule"
  schedule_expression = "cron(0 10 * * ? *)" # 10AM GMT
}

data "aws_vpc" "default" { default = true }
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*Public*", "*public*"]
  }
}

resource "aws_cloudwatch_event_target" "ecs" {
  rule      = aws_cloudwatch_event_rule.scraper_schedule.name
  target_id = "movie-alerts"
  arn       = aws_ecs_cluster.main.arn
  role_arn  = aws_iam_role.eventbridge_ecs.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.scraper.arn
    task_count          = 1
    launch_type         = "FARGATE"
    platform_version    = "1.4.0"
    network_configuration {
      subnets          = data.aws_subnets.public.ids
      security_groups  = [aws_security_group.ecs_task.id]
      assign_public_ip = true
    }
  }
}
