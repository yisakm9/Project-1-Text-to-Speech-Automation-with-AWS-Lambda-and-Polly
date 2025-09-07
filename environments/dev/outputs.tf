output "notes_bucket" {
  description = "Name of the S3 bucket for text notes."
  value       = module.s3_buckets.notes_bucket_id
}

output "audio_bucket" {
  description = "Name of the S3 bucket for generated audio files."
  value       = module.s3_buckets.audio_bucket_id
}

output "api_endpoint" {
  description = "The full invocation URL for the API endpoint."
  value       = "${module.api_gateway.api_endpoint}/generate"
}