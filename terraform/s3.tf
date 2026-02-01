resource "aws_s3_bucket" "movie_lists" {
  bucket = "movie-lists"

  tags = {
    Name        = "movie lists"
    Environment = "Dev"
  }
}
