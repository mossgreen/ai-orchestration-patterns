output "api_endpoint" {
  description = "API Gateway endpoint URL (user-facing)"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "manager_function_name" {
  description = "Manager Lambda function name"
  value       = aws_lambda_function.manager.function_name
}

output "manager_function_arn" {
  description = "Manager Lambda function ARN"
  value       = aws_lambda_function.manager.arn
}

output "availability_function_name" {
  description = "Availability Specialist Lambda function name"
  value       = aws_lambda_function.availability.function_name
}

output "availability_function_url" {
  description = "Availability Specialist Lambda URL (internal)"
  value       = aws_lambda_function_url.availability.function_url
}

output "booking_function_name" {
  description = "Booking Specialist Lambda function name"
  value       = aws_lambda_function.booking.function_name
}

output "booking_function_url" {
  description = "Booking Specialist Lambda URL (internal)"
  value       = aws_lambda_function_url.booking.function_url
}

output "secret_arn" {
  description = "Secrets Manager secret ARN for OpenAI API key"
  value       = aws_secretsmanager_secret.openai_api_key.arn
}

output "setup_instructions" {
  description = "Instructions for testing the deployment"
  value       = <<-EOT

    Pattern G deployed successfully!

    Architecture:
      Manager Lambda:      ${aws_lambda_function.manager.function_name}
      Availability Lambda: ${aws_lambda_function.availability.function_name}
      Booking Lambda:      ${aws_lambda_function.booking.function_name}

    API Endpoint (user-facing): ${aws_apigatewayv2_api.api.api_endpoint}

    Internal URLs (used by Manager):
      Availability: ${aws_lambda_function_url.availability.function_url}
      Booking:      ${aws_lambda_function_url.booking.function_url}

    Test endpoints:
      Health: curl ${aws_apigatewayv2_api.api.api_endpoint}/health
      Chat:   curl -X POST ${aws_apigatewayv2_api.api.api_endpoint}/chat \
                -H "Content-Type: application/json" \
                -d '{"message": "Book tomorrow at 3pm"}'

    View logs:
      Manager:      aws logs tail /aws/lambda/ai-patterns-pattern-g-manager --follow
      Availability: aws logs tail /aws/lambda/ai-patterns-pattern-g-availability --follow
      Booking:      aws logs tail /aws/lambda/ai-patterns-pattern-g-booking --follow
  EOT
}
