

variable "environment_tags" {
  description = "A map of tags to apply to resources for the specific environment."
  type        = map(string)
  default     = {}
}