variable "api_name" {
  description = "The name for the API Gateway."
  type        = string
}

variable "lambda_function_arn" {
  description = "The ARN of the Lambda function for integration."
  type        = string
}

variable "tags" {
  description = "A map of tags to apply to the API."
  type        = map(string)
  default     = {}
}