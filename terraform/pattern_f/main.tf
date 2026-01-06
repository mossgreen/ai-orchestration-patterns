terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local backend - state stored in terraform.tfstate (gitignored)
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# ========================================
# Secrets Manager for OpenAI API Key
# ========================================

resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "ai-patterns-pattern-f-openai-key"
  description             = "OpenAI API key for Pattern F"
  recovery_window_in_days = 0

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-f"
  }
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

# ========================================
# IAM Role for Lambda
# ========================================

resource "aws_iam_role" "lambda_role" {
  name = "ai-patterns-pattern-f-lambda-role"

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
    Part    = "pattern-f"
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "ai-patterns-pattern-f-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # CloudWatch Logs
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda_logs.arn}:*"
      },
      # Secrets Manager
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.openai_api_key.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ========================================
# Lambda Function
# ========================================

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/ai-patterns-pattern-f"
  retention_in_days = var.log_retention_days

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-f"
  }
}

resource "aws_lambda_function" "api" {
  function_name = "ai-patterns-pattern-f"
  description   = "Pattern F: Multi-Agent (Single-Process) - Manager routes to specialist agents"

  role = aws_iam_role.lambda_role.arn

  filename         = "${path.module}/../../pattern-f-multi-agent-single-process/dist/lambda.zip"
  source_code_hash = fileexists("${path.module}/../../pattern-f-multi-agent-single-process/dist/lambda.zip") ? filebase64sha256("${path.module}/../../pattern-f-multi-agent-single-process/dist/lambda.zip") : null

  handler     = "src.lambda_handler.handler"
  runtime     = "python3.12"
  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory

  environment {
    variables = {
      OPENAI_SECRET_ARN = aws_secretsmanager_secret.openai_api_key.arn
      OPENAI_MODEL      = var.openai_model
    }
  }

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-f"
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy.lambda_policy,
  ]
}

# ========================================
# HTTP API Gateway
# ========================================

resource "aws_apigatewayv2_api" "api" {
  name          = "ai-patterns-pattern-f-api"
  protocol_type = "HTTP"
  description   = "Pattern F: Multi-Agent (Single-Process) API"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-f"
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.api.invoke_arn

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-f"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
