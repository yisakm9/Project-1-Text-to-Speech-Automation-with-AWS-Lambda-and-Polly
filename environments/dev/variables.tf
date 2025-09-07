variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function."
  type        = string
  default     = "voicevault-processor-dev"
}

variable "environment_tags" {
  description = "A map of tags to apply to resources for the specific environment."
  type        = map(string)
  default     = {}
}