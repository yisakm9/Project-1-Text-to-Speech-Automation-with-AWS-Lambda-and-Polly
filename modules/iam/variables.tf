variable "role_name" {
  description = "The name for the IAM role."
  type        = string
}

variable "notes_bucket_arn" {
  description = "The ARN of the S3 bucket for input notes."
  type        = string
}

variable "audio_bucket_arn" {
  description = "The ARN of the S3 bucket for output audio."
  type        = string
}

variable "tags" {
  description = "A map of tags to apply to the IAM role."
  type        = map(string)
  default     = {}
}