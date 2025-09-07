# Deploys the Lambda function, setting its environment variables and role.
# Also creates permissions to allow invocation from S3 and API Gateway.

resource "aws_lambda_function" "voicevault" {
  function_name    = var.function_name
  role             = var.lambda_role_arn
  handler          = var.handler
  runtime          = var.runtime
  filename         = var.zip_file_path
  source_code_hash = filebase64sha256(var.zip_file_path)

  environment {
    variables = {
      AUDIO_BUCKET = var.audio_bucket_id
    }
  }

  tags = var.tags
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.voicevault.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.source_s3_bucket_arn
}

resource "aws_lambda_permission" "allow_apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.voicevault.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = var.api_gateway_execution_arn
}

