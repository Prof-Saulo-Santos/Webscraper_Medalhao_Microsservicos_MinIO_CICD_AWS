variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "arxiv-project"
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
  default     = "dev"
}
