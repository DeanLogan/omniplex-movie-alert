output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.movie_alerts.repository_url
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for movie lists"
  value       = aws_s3_bucket.movie_lists.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = aws_ecs_task_definition.scraper.arn
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.scraper_schedule.name
}
