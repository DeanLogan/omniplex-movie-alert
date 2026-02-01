resource "aws_ecs_cluster" "main" {
  name = "movie-alerts-cluster"
  
  tags = {
    App = "movie-alerts"
  }
}

resource "aws_security_group" "ecs_task" {
  name        = "movie-alerts-ecs-task-sg"
  description = "Security group for movie alerts ECS task"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "movie-alerts-ecs-task"
  }
}

resource "aws_cloudwatch_log_group" "scraper" {
  name              = "/ecs/movie-alerts"
  retention_in_days = 7
}