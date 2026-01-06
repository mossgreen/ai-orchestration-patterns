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
  name                    = "ai-patterns-pattern-g-openai-key"
  description             = "OpenAI API key for Pattern G"
  recovery_window_in_days = 0

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
  }
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

# ========================================
# IAM Roles for Lambda Functions
# ========================================

# Shared IAM role for all three Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "ai-patterns-pattern-g-lambda-role"

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
    Part    = "pattern-g"
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "ai-patterns-pattern-g-lambda-policy"
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
        Resource = [
          "${aws_cloudwatch_log_group.manager_logs.arn}:*",
          "${aws_cloudwatch_log_group.availability_logs.arn}:*",
          "${aws_cloudwatch_log_group.booking_logs.arn}:*"
        ]
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
# CloudWatch Log Groups
# ========================================

resource "aws_cloudwatch_log_group" "manager_logs" {
  name              = "/aws/lambda/ai-patterns-pattern-g-manager"
  retention_in_days = var.log_retention_days

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
    Service = "manager"
  }
}

resource "aws_cloudwatch_log_group" "availability_logs" {
  name              = "/aws/lambda/ai-patterns-pattern-g-availability"
  retention_in_days = var.log_retention_days

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
    Service = "availability"
  }
}

resource "aws_cloudwatch_log_group" "booking_logs" {
  name              = "/aws/lambda/ai-patterns-pattern-g-booking"
  retention_in_days = var.log_retention_days

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
    Service = "booking"
  }
}

# ========================================
# Lambda Functions - Specialists (deployed first)
# ========================================

resource "aws_lambda_function" "availability" {
  function_name = "ai-patterns-pattern-g-availability"
  description   = "Pattern G: Availability Specialist - Checks available slots"

  role = aws_iam_role.lambda_role.arn

  filename         = "${path.module}/../../pattern-g-multi-agent-multi-process/dist/availability/lambda.zip"
  source_code_hash = fileexists("${path.module}/../../pattern-g-multi-agent-multi-process/dist/availability/lambda.zip") ? filebase64sha256("${path.module}/../../pattern-g-multi-agent-multi-process/dist/availability/lambda.zip") : null

  handler     = "src.availability.lambda_handler.handler"
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
    Part    = "pattern-g"
    Service = "availability"
  }

  depends_on = [
    aws_cloudwatch_log_group.availability_logs,
    aws_iam_role_policy.lambda_policy,
  ]
}

resource "aws_lambda_function" "booking" {
  function_name = "ai-patterns-pattern-g-booking"
  description   = "Pattern G: Booking Specialist - Books slots"

  role = aws_iam_role.lambda_role.arn

  filename         = "${path.module}/../../pattern-g-multi-agent-multi-process/dist/booking/lambda.zip"
  source_code_hash = fileexists("${path.module}/../../pattern-g-multi-agent-multi-process/dist/booking/lambda.zip") ? filebase64sha256("${path.module}/../../pattern-g-multi-agent-multi-process/dist/booking/lambda.zip") : null

  handler     = "src.booking.lambda_handler.handler"
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
    Part    = "pattern-g"
    Service = "booking"
  }

  depends_on = [
    aws_cloudwatch_log_group.booking_logs,
    aws_iam_role_policy.lambda_policy,
  ]
}

# ========================================
# Lambda Function URLs for Specialists
# ========================================

resource "aws_lambda_function_url" "availability" {
  function_name      = aws_lambda_function.availability.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
    allow_headers = ["Content-Type"]
    max_age       = 300
  }
}

resource "aws_lambda_function_url" "booking" {
  function_name      = aws_lambda_function.booking.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
    allow_headers = ["Content-Type"]
    max_age       = 300
  }
}

# ========================================
# Lambda Function - Manager (deployed after specialists)
# ========================================

resource "aws_lambda_function" "manager" {
  function_name = "ai-patterns-pattern-g-manager"
  description   = "Pattern G: Manager - Routes to specialist services via HTTP"

  role = aws_iam_role.lambda_role.arn

  filename         = "${path.module}/../../pattern-g-multi-agent-multi-process/dist/manager/lambda.zip"
  source_code_hash = fileexists("${path.module}/../../pattern-g-multi-agent-multi-process/dist/manager/lambda.zip") ? filebase64sha256("${path.module}/../../pattern-g-multi-agent-multi-process/dist/manager/lambda.zip") : null

  handler     = "src.manager.lambda_handler.handler"
  runtime     = "python3.12"
  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory

  environment {
    variables = {
      OPENAI_SECRET_ARN = aws_secretsmanager_secret.openai_api_key.arn
      OPENAI_MODEL      = var.openai_model
      AVAILABILITY_URL  = aws_lambda_function_url.availability.function_url
      BOOKING_URL       = aws_lambda_function_url.booking.function_url
    }
  }

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
    Service = "manager"
  }

  depends_on = [
    aws_cloudwatch_log_group.manager_logs,
    aws_iam_role_policy.lambda_policy,
    aws_lambda_function_url.availability,
    aws_lambda_function_url.booking,
  ]
}

# ========================================
# HTTP API Gateway (for Manager only)
# ========================================

resource "aws_apigatewayv2_api" "api" {
  name          = "ai-patterns-pattern-g-api"
  protocol_type = "HTTP"
  description   = "Pattern G: Multi-Agent Multi-Process API"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
  }
}

resource "aws_apigatewayv2_integration" "manager" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.manager.invoke_arn

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.manager.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Project = "ai-patterns"
    Part    = "pattern-g"
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.manager.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
