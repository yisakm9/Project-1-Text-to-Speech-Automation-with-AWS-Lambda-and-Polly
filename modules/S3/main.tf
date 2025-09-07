# Creates two S3 buckets with a common prefix and random suffix.
# Tags are applied to both buckets for resource tracking.

resource "aws_s3_bucket" "notes" {
  bucket = "${var.bucket_name_prefix}-notes-${var.random_suffix}"
  tags   = var.tags
}

resource "aws_s3_bucket" "audio" {
  bucket = "${var.bucket_name_prefix}-audio-${var.random_suffix}"
  tags   = var.tags
}