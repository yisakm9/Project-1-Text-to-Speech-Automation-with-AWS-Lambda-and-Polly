# Deploys the Lambda function, setting its environment variables and role.
# Also creates permissions to allow invocation from S3 and API Gateway.
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_code_directory
  output_path = "${path.root}/lambda_function.zip" # Creates the zip in the root's temp dir
}

resource "aws_lambda_function" "voicevault" {
  function_name    = var.function_name
  role             = var.lambda_role_arn
  handler          = var.handler
  runtime          = var.runtime
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

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

