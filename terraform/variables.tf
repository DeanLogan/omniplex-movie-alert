variable "gmail_app_password" {
  description = "Gmail app password for movie scraper"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "error_email" {
  description = "Email for error notifications"
  type        = string
}

variable "sender_email" {
  description = "Email address for sending notifications"
  type        = string
}