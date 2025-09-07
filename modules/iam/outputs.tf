output "lambda_role_arn" {
  description = "The ARN of the created IAM role for the Lambda function."
  value       = aws_iam_role.lambda_role.arn
}