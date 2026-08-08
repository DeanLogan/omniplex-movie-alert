output "s3_bucket_name" {
  description = "Name of the S3 bucket for movie lists"
  value       = aws_s3_bucket.movie_lists.id
}
