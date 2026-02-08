variable "project_name" {
  type    = string
  default = "crm-approval"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "lambda_source_dir" {
  type    = string
  default = "../../backend"
}

variable "database_url" {
  type = string
}

variable "s3_bucket" {
  type    = string
  default = "crm-project-contracts"
}

variable "storage_mode" {
  type    = string
  default = "local"
}
