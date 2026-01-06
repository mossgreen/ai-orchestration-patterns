terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ========================================
# IAM Role for Bedrock Agent
# ========================================

resource "aws_iam_role" "bedrock_agent_role" {
  name = "ai-patterns-pattern-h-bedrock-agent-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
  }
}

resource "aws_iam_role_policy" "bedrock_agent_policy" {
  name = "ai-patterns-pattern-h-bedrock-agent-policy"
  role = aws_iam_role.bedrock_agent_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.foundation_model}"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.action.arn
      }
    ]
  })
}

# ========================================
# IAM Role for Lambda Functions
# ========================================

resource "aws_iam_role" "lambda_role" {
  name = "ai-patterns-pattern-h-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "ai-patterns-pattern-h-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "${aws_cloudwatch_log_group.action_logs.arn}:*",
          "${aws_cloudwatch_log_group.invoker_logs.arn}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeAgent"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ========================================
# CloudWatch Log Groups
# ========================================

resource "aws_cloudwatch_log_group" "action_logs" {
  name              = "/aws/lambda/ai-patterns-pattern-h-action"
  retention_in_days = var.log_retention_days

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
    Service = "action"
  }
}

resource "aws_cloudwatch_log_group" "invoker_logs" {
  name              = "/aws/lambda/ai-patterns-pattern-h-invoker"
  retention_in_days = var.log_retention_days

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
    Service = "invoker"
  }
}

# ========================================
# Lambda Functions
# ========================================

resource "aws_lambda_function" "action" {
  function_name = "ai-patterns-pattern-h-action"
  description   = "Pattern H: Bedrock Agent Action Group Handler"

  role = aws_iam_role.lambda_role.arn

  filename         = "${path.module}/../../pattern-h-bedrock-agent/dist/action/lambda.zip"
  source_code_hash = fileexists("${path.module}/../../pattern-h-bedrock-agent/dist/action/lambda.zip") ? filebase64sha256("${path.module}/../../pattern-h-bedrock-agent/dist/action/lambda.zip") : null

  handler     = "src.action.lambda_handler.handler"
  runtime     = "python3.12"
  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
    Service = "action"
  }

  depends_on = [
    aws_cloudwatch_log_group.action_logs,
    aws_iam_role_policy.lambda_policy,
  ]
}

resource "aws_lambda_permission" "bedrock_invoke_action" {
  statement_id  = "AllowBedrockInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.action.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent/*"
}

resource "aws_lambda_function" "invoker" {
  function_name = "ai-patterns-pattern-h-invoker"
  description   = "Pattern H: Bedrock Agent Invoker (User-facing API)"

  role = aws_iam_role.lambda_role.arn

  filename         = "${path.module}/../../pattern-h-bedrock-agent/dist/invoker/lambda.zip"
  source_code_hash = fileexists("${path.module}/../../pattern-h-bedrock-agent/dist/invoker/lambda.zip") ? filebase64sha256("${path.module}/../../pattern-h-bedrock-agent/dist/invoker/lambda.zip") : null

  handler     = "src.invoker.lambda_handler.handler"
  runtime     = "python3.12"
  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory

  environment {
    variables = {
      BEDROCK_AGENT_ID       = aws_bedrockagent_agent.booking.agent_id
      BEDROCK_AGENT_ALIAS_ID = aws_bedrockagent_agent_alias.prod.agent_alias_id
      AWS_REGION_NAME        = var.aws_region
    }
  }

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
    Service = "invoker"
  }

  depends_on = [
    aws_cloudwatch_log_group.invoker_logs,
    aws_iam_role_policy.lambda_policy,
    aws_bedrockagent_agent_alias.prod,
  ]
}

# ========================================
# Bedrock Agent
# ========================================

resource "aws_bedrockagent_agent" "booking" {
  agent_name                  = "ai-patterns-pattern-h-agent"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  foundation_model            = var.foundation_model
  idle_session_ttl_in_seconds = 900
  prepare_agent               = true

  instruction = <<-EOT
    You are a helpful tennis court booking assistant.

    Your job is to help users:
    1. Check available tennis court slots for specific dates and times
    2. Book tennis court slots for them

    WORKFLOW:
    - When a user wants to book, FIRST use check_availability to find available slots
    - Present the available options clearly with their slot IDs
    - When the user confirms a slot, use book_slot with the slot_id to complete the booking
    - Always confirm the booking details after a successful booking

    GUIDELINES:
    - Convert relative dates like "tomorrow" or "next Monday" to YYYY-MM-DD format
    - If no specific time is mentioned, show all available slots for the day
    - Be concise but friendly
    - Always use the action group tools to check real availability - never make up slots
  EOT

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
  }
}

resource "aws_bedrockagent_agent_action_group" "booking_actions" {
  agent_id          = aws_bedrockagent_agent.booking.agent_id
  agent_version     = "DRAFT"
  action_group_name = "BookingActions"
  description       = "Actions for checking availability and booking tennis courts"

  action_group_executor {
    lambda = aws_lambda_function.action.arn
  }

  api_schema {
    payload = file("${path.module}/../../pattern-h-bedrock-agent/openapi-schema.json")
  }

  depends_on = [
    aws_lambda_permission.bedrock_invoke_action
  ]
}

resource "aws_bedrockagent_agent_alias" "prod" {
  agent_id         = aws_bedrockagent_agent.booking.agent_id
  agent_alias_name = "prod"
  description      = "Production alias for Pattern H booking agent"

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
  }

  depends_on = [
    aws_bedrockagent_agent_action_group.booking_actions
  ]
}

# ========================================
# HTTP API Gateway (user-facing)
# ========================================

resource "aws_apigatewayv2_api" "api" {
  name          = "ai-patterns-pattern-h-api"
  protocol_type = "HTTP"
  description   = "Pattern H: Bedrock Agent API"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
  }
}

resource "aws_apigatewayv2_integration" "invoker" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.invoker.invoke_arn

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.invoker.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-h"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.invoker.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
