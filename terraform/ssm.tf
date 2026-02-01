resource "aws_ssm_parameter" "gmail_app_password" {
  name        = "/movie-alerts/prod/gmail_app_password"
  description = "Gmail app password for movie alerts"
  type        = "SecureString"

  value = var.gmail_app_password

  overwrite = false

  tags = {
    App     = "movie-alerts"
    Env     = "prod"
    Managed = "terraform"
  }
}

resource "aws_ssm_parameter" "error_email" {
  name        = "/movie-alerts/prod/error_email"
  description = "Error notification email"
  type        = "String"
  value       = var.error_email

  tags = {
    App     = "movie-alerts"
    Env     = "prod"
    Managed = "terraform"
  }
}

resource "aws_ssm_parameter" "sender_email" {
  name        = "/movie-alerts/prod/sender_email"
  description = "Sender email address"
  type        = "String"
  value       = var.sender_email

  tags = {
    App     = "movie-alerts"
    Env     = "prod"
    Managed = "terraform"
  }
}