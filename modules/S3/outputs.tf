output "notes_bucket_id" {
  description = "The ID (name) of the notes S3 bucket."
  value       = aws_s3_bucket.notes.id
}

output "notes_bucket_arn" {
  description = "The ARN of the notes S3 bucket."
  value       = aws_s3_bucket.notes.arn
}

output "audio_bucket_id" {
  description = "The ID (name) of the audio S3 bucket."
  value       = aws_s3_bucket.audio.id
}

output "audio_bucket_arn" {
  description = "The ARN of the audio S3 bucket."
  value       = aws_s3_bucket.audio.arn
}