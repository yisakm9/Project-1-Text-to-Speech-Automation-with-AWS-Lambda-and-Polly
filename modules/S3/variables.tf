variable "bucket_name_prefix" {
  description = "The prefix for the S3 bucket names."
  type        = string
  default     = "voicevault"
}

variable "random_suffix" {
  description = "A random string to ensure bucket name uniqueness."
  type        = string
}

variable "tags" {
  description = "A map of tags to apply to the buckets."
  type        = map(string)
  default     = {}
}