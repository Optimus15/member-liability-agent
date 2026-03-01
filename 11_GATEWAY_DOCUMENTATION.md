# AWS API Gateway Setup Documentation

## Overview

This document describes the AWS API Gateway setup for the Member Liability Agent. The setup creates a REST API Gateway named `ReturnsRefundsGateway` with Cognito authentication and IAM role integration for Lambda function invocation.

## Purpose

The API Gateway provides:
- **RESTful API**: HTTP endpoints for the Member Liability Agent
- **Cognito Authentication**: Secure access using OAuth 2.0 tokens
- **Lambda Integration**: Seamless connection to backend Lambda functions
- **Regional Deployment**: Low-latency access within the AWS region

## Architecture

```
┌─────────────────┐
│     Client      │
└────────┬────────┘
         │ 1. Request with Bearer Token
         ▼
┌─────────────────────────┐
│  API Gateway            │
│  ReturnsRefundsGateway  │
│  ┌──────────────────┐   │
│  │ Cognito Auth     │   │
│  │ Authorizer       │   │
│  └──────────────────┘   │
│  ┌──────────────────┐   │
│  │ API Resources    │   │
│  │ /liability       │   │
│  │ /eligibility     │   │
│  └──────────────────┘   │
└────────┬────────────────┘
         │ 2. Invoke with IAM Role
         ▼
┌─────────────────┐
│ Lambda Functions│
│ - check_elig... │
│ - calculate_... │
└─────────────────┘
```

## Components Created

### 1. REST API Gateway
- **Name**: `ReturnsRefundsGateway`
- **Type**: REST API
- **Endpoint**: REGIONAL
- **Description**: API Gateway for Member Liability Agent with Cognito authentication

### 2. Cognito Authorizer
- **Name**: `CognitoAuthorizer`
- **Type**: COGNITO_USER_POOLS
- **Identity Source**: `method.request.header.Authorization`
- **Cache TTL**: 300 seconds (5 minutes)
- **Purpose**: Validates OAuth 2.0 access tokens from Cognito

### 3. Configuration Files

#### gateway_config.json
Contains the API Gateway configuration:
```json
{
  "api_id": "xxxxxxxxxx",
  "api_name": "ReturnsRefundsGateway",
  "api_url": "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod",
  "authorizer_id": "xxxxxxxxxx",
  "region": "us-east-1",
  "stage": "prod",
  "created_at": "2026-02-28T17:39:49.800009"
}
```

#### gateway_role_config.json
Contains the IAM role configuration:
```json
{
  "role_arn": "arn:aws:iam::123456789012:role/GatewayLambdaInvokeRole",
  "role_name": "GatewayLambdaInvokeRole",
  "created_at": "2026-02-28T17:39:49.799467"
}
```

## Prerequisites

Before running the script, ensure you have:

1. **Cognito Configuration**: Run `08_create_cognito.py` first
   - Creates User Pool
   - Generates OAuth credentials
   - Saves to `cognito_config.json`

2. **IAM Role Configuration**: Run `09_create_gateway_role.py` first
   - Creates IAM role for Lambda invocation
   - Grants necessary permissions
   - Saves to `gateway_role_config.json`

3. **AWS Credentials**: Configured with appropriate permissions
   - `apigateway:POST` (create REST API)
   - `apigateway:GET` (read API details)
   - `apigateway:PUT` (update API configuration)

## Usage

### Production Script: `11_create_gateway.py`

Creates actual AWS resources:

```bash
cd 01_member_liability_agent
python3 11_create_gateway.py
```

**Steps performed:**
1. Load Cognito configuration
2. Load IAM role configuration
3. Create REST API Gateway
4. Create Cognito authorizer
5. Generate API URL
6. Save configuration

### Dry-Run Script: `11_create_gateway_dryrun.py`

Simulates the setup without AWS credentials:

```bash
cd 01_member_liability_agent
python3 11_create_gateway_dryrun.py
```

**Benefits:**
- No AWS credentials required
- Tests script logic
- Generates sample configuration
- Shows what would be created

## Post-Setup Configuration

After creating the API Gateway, you need to:

### 1. Create API Resources

Add endpoints to your API:

```bash
# Get root resource ID
aws apigateway get-resources \
  --rest-api-id <api_id>

# Create /liability resource
aws apigateway create-resource \
  --rest-api-id <api_id> \
  --parent-id <root_resource_id> \
  --path-part liability
```

### 2. Create API Methods

Add HTTP methods to resources:

```bash
# Create POST method on /liability
aws apigateway put-method \
  --rest-api-id <api_id> \
  --resource-id <resource_id> \
  --http-method POST \
  --authorization-type COGNITO_USER_POOLS \
  --authorizer-id <authorizer_id>
```

### 3. Integrate with Lambda

Connect methods to Lambda functions:

```bash
# Create Lambda integration
aws apigateway put-integration \
  --rest-api-id <api_id> \
  --resource-id <resource_id> \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:<region>:lambda:path/2015-03-31/functions/<lambda_arn>/invocations \
  --credentials <role_arn>
```

### 4. Deploy the API

Deploy to a stage to activate:

```bash
aws apigateway create-deployment \
  --rest-api-id <api_id> \
  --stage-name prod \
  --description "Production deployment"
```

### 5. Test the API

Test with a Cognito access token:

```bash
# Get access token first (from Cognito)
curl -X POST https://<domain_prefix>.auth.<region>.amazoncognito.com/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials' \
  -d 'client_id=<client_id>' \
  -d 'client_secret=<client_secret>' \
  -d 'scope=member-liability-api/read member-liability-api/write'

# Use access token to call API
curl -X POST https://<api_id>.execute-api.<region>.amazonaws.com/prod/liability \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"member_id": "12345", "claim_amount": 1000}'
```

## API Gateway Features

### Request Flow

1. **Client Request**: Client sends HTTP request with Bearer token
2. **Authorization**: Cognito authorizer validates the token
3. **Caching**: Authorization result cached for 5 minutes
4. **Lambda Invocation**: API Gateway invokes Lambda with IAM role
5. **Response**: Lambda response returned to client

### Security Features

- **Cognito Authentication**: OAuth 2.0 token validation
- **IAM Role**: Least-privilege access to Lambda functions
- **HTTPS Only**: All traffic encrypted in transit
- **Regional Endpoint**: Data stays within AWS region

### Performance Features

- **Authorization Caching**: Reduces Cognito API calls
- **Lambda Proxy Integration**: Minimal latency
- **Regional Deployment**: Low-latency access

## Troubleshooting

### API Gateway Creation Fails

**Problem**: `create_rest_api()` returns error

**Solutions**:
1. Verify AWS credentials are configured
2. Check IAM permissions for `apigateway:POST`
3. Ensure region is correctly set
4. Check API Gateway service limits

### Cognito Authorizer Creation Fails

**Problem**: `create_authorizer()` returns error

**Solutions**:
1. Verify Cognito User Pool exists
2. Check User Pool ARN is correct
3. Ensure IAM permissions for `apigateway:POST`
4. Verify identity source format

### Configuration File Not Found

**Problem**: Script cannot find `cognito_config.json` or `gateway_role_config.json`

**Solutions**:
1. Run `08_create_cognito.py` first
2. Run `09_create_gateway_role.py` first
3. Check file paths are correct
4. Verify files are in the same directory

### API Returns 401 Unauthorized

**Problem**: API calls fail with 401 error

**Solutions**:
1. Verify access token is valid (not expired)
2. Check token is included in Authorization header
3. Ensure authorizer is attached to method
4. Verify Cognito User Pool is active

## Best Practices

### Security

1. **Use HTTPS Only**: Never allow HTTP traffic
2. **Rotate Credentials**: Regularly rotate Cognito client secrets
3. **Monitor Access**: Enable CloudWatch logging
4. **Least Privilege**: Use minimal IAM permissions

### Performance

1. **Enable Caching**: Cache authorization results
2. **Use Lambda Proxy**: Minimize integration overhead
3. **Regional Deployment**: Deploy close to users
4. **Optimize Lambda**: Keep functions warm

### Cost Optimization

1. **Cache Authorization**: Reduce Cognito API calls
2. **Monitor Usage**: Track API Gateway requests
3. **Set Throttling**: Prevent unexpected costs
4. **Use Stages**: Separate dev/test/prod

## Next Steps

1. ✅ API Gateway created
2. ⏳ **Create API resources** (endpoints)
3. ⏳ **Create API methods** (GET, POST, etc.)
4. ⏳ **Integrate with Lambda** functions
5. ⏳ **Deploy to stage** (prod)
6. ⏳ **Test end-to-end** with Cognito token

## References

- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [API Gateway REST API Reference](https://docs.aws.amazon.com/apigateway/latest/api/)
- [Cognito Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html)
- [Lambda Proxy Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html)
