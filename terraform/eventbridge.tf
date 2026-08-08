resource "aws_iam_role" "eventbridge_ecs" {
  name = "movie-alerts-eventbridge-ecs-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
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
    name   = "map-public-ip-on-launch"
    values = ["true"]
  }
}
