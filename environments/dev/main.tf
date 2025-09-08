# This is the root module for the 'dev' environment. It defines the provider
# and orchestrates the child modules, passing outputs from one as inputs to another.

provider "aws" {
  region = var.aws_region
}

resource "random_id" "suffix" {
  byte_length = 4
}

module "s3_buckets" {
  source           = "../../modules/S3"
  random_suffix    = random_id.suffix.hex
  tags             = var.environment_tags
}

module "iam" {
  source           = "../../modules/iam"
  role_name        = "voicevault-lambda-role-dev"
  notes_bucket_arn = module.s3_buckets.notes_bucket_arn
  audio_bucket_arn = module.s3_buckets.audio_bucket_arn
  tags             = var.environment_tags
}

module "api_gateway" {
  source              = "../../modules/api_gateway"
  api_name            = "voicevault-api-dev"
  lambda_function_arn = module.lambda.function_arn
  tags                = var.environment_tags
}

module "lambda" {
  source                      = "../../modules/lambda_function"
  function_name               = var.lambda_function_name
  source_code_directory       = "${path.root}/../../src/lambda_function"
  lambda_role_arn             = module.iam.lambda_role_arn
  audio_bucket_id             = module.s3_buckets.audio_bucket_id
  source_s3_bucket_arn        = module.s3_buckets.notes_bucket_arn
  api_gateway_execution_arn   = "${module.api_gateway.execution_arn}/*/*"
  tags                        = var.environment_tags
}

# The  S3 notification resource connects the S3 and Lambda modules,
# so it is defined here in the root module to avoid circular dependencies.
resource "aws_s3_bucket_notification" "notes_notification" {
  bucket = module.s3_buckets.notes_bucket_id

  lambda_function {
    lambda_function_arn = module.lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
  }

  # Ensure the Lambda permission is created before the notification is attached.
  depends_on = [
    module.lambda.allow_s3
  ]
}