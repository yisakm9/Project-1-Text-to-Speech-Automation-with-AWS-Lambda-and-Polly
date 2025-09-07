# Creates the IAM Role and attaches a policy that grants the Lambda
# function permissions to interact with S3, Polly, and CloudWatch Logs.

resource "aws_iam_role" "lambda_role" {
  name               = var.role_name
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "lambda_policy" {
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:GetObject", "s3:PutObject"],
        Resource = [
          var.notes_bucket_arn,
          "${var.notes_bucket_arn}/*",
          var.audio_bucket_arn,
          "${var.audio_bucket_arn}/*"
        ]
      },
      {
        Effect   = "Allow",
        Action   = ["polly:SynthesizeSpeech"],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}