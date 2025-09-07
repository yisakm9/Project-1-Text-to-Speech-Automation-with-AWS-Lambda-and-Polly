# modules/api_gateway/outputs.tf
output "api_endpoint" {
description = "The invocation endpoint for the API."
value = aws_apigatewayv2_api.api.api_endpoint
}
output "execution_arn" {
description = "The execution ARN of the API Gateway, used for permissions."
value = aws_apigatewayv2_api.api.execution_arn
}