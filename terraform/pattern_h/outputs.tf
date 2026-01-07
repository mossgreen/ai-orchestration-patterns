output "api_endpoint" {
  description = "API Gateway endpoint URL (user-facing)"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "agent_id" {
  description = "Bedrock Agent ID"
  value       = aws_bedrockagent_agent.booking.agent_id
}

output "agent_alias_id" {
  description = "Bedrock Agent Alias ID"
  value       = aws_bedrockagent_agent_alias.prod.agent_alias_id
}

output "action_lambda_name" {
  description = "Action Lambda function name"
  value       = aws_lambda_function.action.function_name
}

output "action_lambda_arn" {
  description = "Action Lambda function ARN"
  value       = aws_lambda_function.action.arn
}

output "invoker_lambda_name" {
  description = "Invoker Lambda function name"
  value       = aws_lambda_function.invoker.function_name
}

output "invoker_lambda_arn" {
  description = "Invoker Lambda function ARN"
  value       = aws_lambda_function.invoker.arn
}

output "setup_instructions" {
  description = "Instructions for testing the deployment"
  value       = <<-EOT

    Pattern H (Bedrock Agent) deployed successfully!

    Architecture:
      Bedrock Agent:   ${aws_bedrockagent_agent.booking.agent_id}
      Agent Alias:     ${aws_bedrockagent_agent_alias.prod.agent_alias_id}
      Action Lambda:   ${aws_lambda_function.action.function_name}
      Invoker Lambda:  ${aws_lambda_function.invoker.function_name}

    API Endpoint: ${aws_apigatewayv2_api.api.api_endpoint}

    Test endpoints:
      Health: curl ${aws_apigatewayv2_api.api.api_endpoint}/health
      Chat:   curl -X POST ${aws_apigatewayv2_api.api.api_endpoint}/chat \
                -H "Content-Type: application/json" \
                -d '{"message": "Book tomorrow at 3pm"}'

    View logs:
      Action:  aws logs tail /aws/lambda/ai-patterns-pattern-h-action --follow
      Invoker: aws logs tail /aws/lambda/ai-patterns-pattern-h-invoker --follow

    Note: Bedrock Agent uses ${var.foundation_model}. Ensure model access is enabled in AWS Console.
  EOT
}
