output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.api.arn
}

output "secret_arn" {
  description = "Secrets Manager secret ARN for OpenAI API key"
  value       = aws_secretsmanager_secret.openai_api_key.arn
}

output "setup_instructions" {
  description = "Instructions for testing the deployment"
  value       = <<-EOT

    Pattern F deployed successfully!

    API Endpoint: ${aws_apigatewayv2_api.api.api_endpoint}
    Lambda:       ${aws_lambda_function.api.function_name}

    Test endpoints:
      Health: curl ${aws_apigatewayv2_api.api.api_endpoint}/health
      Chat:   curl -X POST ${aws_apigatewayv2_api.api.api_endpoint}/chat \
                -H "Content-Type: application/json" \
                -d '{"message": "Book tomorrow at 3pm"}'

    View logs:
      aws logs tail /aws/lambda/ai-patterns-pattern-f --follow
  EOT
}
