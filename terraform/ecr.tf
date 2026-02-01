resource "aws_ecr_repository" "movie_alerts" {
  name                 = "movie-alerts"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    App = "movie-alerts"
  }
}
