// for demonstration purposes

provider "aws" {
  region = "eu-centraòl-1"
}

locals {
  project_name = "python-api-lambda"
}

resource "aws_lambda_function" "python-api-function" {
  function_name = "${terraform.workspace}-${local.project_name}"
  handler = "app.handler"
  role = aws_iam_role.lambda_role.arn
  runtime = "python 3.7"
  filename = "./app.zip"
  timeout = var.lambda_timeout
  memory_size = lambda_memory_size
}

resource "aws_iam_role" "lambda_role" {
  name = "${terraform.workspace}-${local.project_name}-lambda-role"
  tags = {
    project = local.project_name
  }
  assume_role_policy = <<EOF
{
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
              "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
          }
        ]
      }
EOF
}

resource "aws_api_gateway_rest_api" "Api" {
  name = "python-api"
  description = "Python REST api with mysql"
}

// root
resource "aws_api_gateway_resource" "Resource" {
  rest_api_id = aws_api_gateway_rest_api.Api.id
  parent_id   = aws_api_gateway_resource.root_resource_id
  path_part   = ""
}

// users
resource "aws_api_gateway_resource" "UserResource" {
  rest_api_id = aws_api_gateway_rest_api.Api.id
  parent_id   = aws_api_gateway_resource.Resource.id
  path_part   = "users"
}

resource "aws_api_gateway_method" "UserLoginMethod" {
  authorization = ""
  http_method = "POST"
  resource_id = aws_api_gateway_rest_api.Api.id
  rest_api_id = aws_api_gateway_resource.UserResource.id
}

resource "aws_api_gateway_resource" "LinkResource" {
  rest_api_id = aws_api_gateway_rest_api.Api.id
  parent_id   = aws_api_gateway_resource.Resource.id
  path_part   = "links"
}

resource "aws_api_gateway_method" "LinkGetMethod" {
  authorization = ""
  http_method = "GET"
  resource_id = aws_api_gateway_rest_api.Api.id
  rest_api_id = aws_api_gateway_resource.LinkResource.id
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.Api.id
  resource_id = aws_api_gateway_resource.Resource.id
  http_method = aws_api_gateway_method.UserLoginMethod.http_method
  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.python-api-function.invoke_arn
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.Api.id
  resource_id = aws_api_gateway_resource.Resource.id
  http_method = aws_api_gateway_method.LinkGetMethod.http_method
  integration_http_method = "GET"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.python-api-function.invoke_arn
}
