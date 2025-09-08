
variable "function_name" {
  description = "The name of the Lambda function."
  type        = string
}

variable "handler" {
  description = "The handler for the Lambda function."
  type        = string
  default     = "lambda_function.lambda_handler"
}

variable "runtime" {
  description = "The runtime for the Lambda function."
  type        = string
  default     = "python3.11"
}


variable "lambda_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  type        = string
}

variable "audio_bucket_id" {
  description = "The ID of the S3 bucket for audio files."
  type        = string
}

variable "source_s3_bucket_arn" {
  description = "The ARN of the S3 bucket that triggers the Lambda."
  type        = string
}

variable "api_gateway_execution_arn" {
  description = "The execution ARN of the API Gateway."
  type        = string
}

variable "tags" {
  description = "A map of tags to apply to the function."
  type        = map(string)
  default     = {}
}

variable "source_code_directory" {
  description = "The local directory path containing the Lambda function source code."
  type        = string
}