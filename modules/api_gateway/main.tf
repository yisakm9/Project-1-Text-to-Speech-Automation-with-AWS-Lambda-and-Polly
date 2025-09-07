# Creates an HTTP API Gateway, a proxy integration to the Lambda function,
# and a route to make the function accessible via a POST request.

resource "aws_apigatewayv2_api" "api" {
  name          = var.api_name
  protocol_type = "HTTP"
  tags          = var.tags
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.lambda_function_arn
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /generate"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}