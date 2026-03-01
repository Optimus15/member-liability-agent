# AWS Cognito Authentication Setup Documentation

## Overview

This document describes the AWS Cognito authentication setup for the Member Liability Gateway. The setup creates a complete OAuth 2.0 authentication system using AWS Cognito User Pools, enabling secure machine-to-machine authentication for the Bedrock Agent.

## Purpose

The Cognito setup provides:
- **Secure Authentication**: OAuth 2.0 client credentials flow for machine-to-machine auth
- **Access Control**: Read/write permissions via custom OAuth scopes
- **Token Management**: Automatic token generation and validation
- **API Gateway Integration**: Ready for API Gateway Cognito authorizer

## Architecture

```
┌─────────────────┐
│  Bedrock Agent  │
└────────┬────────┘
         │ 1. Request Token
         ▼
┌─────────────────────────┐
│  Cognito User Pool      │
│  ┌──────────────────┐   │
│  │ Resource Server  │   │
│  │ - read scope     │   │
│  │ - write scope    │   │
│  └──────────────────┘   │
│  ┌──────────────────┐   │
│  │ App Client       │   │
│  │ - Client ID      │   │
│  │ - Client Secret  │   │
│  └──────────────────┘   │
└────────┬────────────────┘
         │ 2. Return Access Token
         ▼
┌─────────────────┐
│  API Gateway    │
│  (Cognito Auth) │
└────────┬────────┘
         │ 3. Validate Token
         ▼
┌─────────────────┐
│  Backend API    │
└─────────────────┘
```

## Components Created

### 1. Cognito User Pool
- **Name**: `member-liability-gateway-pool`
- **Purpose**: Central authentication service
- **Features**:
  - Password policy enforcement
  - Email verification
  - Advanced security (configurable)

### 2. User Pool Domain
- **Domain Prefix**: `member-liability-gateway`
- **Full Domain**: `member-liability-gateway.auth.{region}.amazoncognito.com`
- **Purpose**: Provides OAuth 2.0 endpoints for token generation

### 3. Resource Server
- **Identifier**: `member-liability-api`
- **Scopes**:
  - `member-liability-api/read`: Read access to member liability data
  - `member-liability-api/write`: Write access to member liability data

### 4. App Client
- **Name**: `member-liability-agent-client`
- **OAuth Flow**: Client Credentials (machine-to-machine)
- **Token Validity**: 60 minutes
- **Features**:
  - Client ID and Secret for authentication
  - Automatic token generation
  - Scope-based access control

## Configuration File

The setup saves all credentials to `cognito_config.json`:

```json
{
  "user_pool_id": "us-east-1_XXXXXXXXX",
  "domain_prefix": "member-liability-gateway",
  "client_id": "xxxxxxxxxxxxxxxxxxxx",
  "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "token_endpoint": "https://member-liability-gateway.auth.us-east-1.amazoncognito.com/oauth2/token",
  "discovery_url": "https://member-liability-gateway.auth.us-east-1.amazoncognito.com/.well-known/openid-configuration",
  "created_at": "2026-02-28T17:25:52.541145",
  "region": "us-east-1"
}
```

### Configuration Keys

| Key | Description |
|-----|-------------|
| `user_pool_id` | The Cognito User Pool ID |
| `domain_prefix` | The domain prefix (NOT "domain") |
| `client_id` | The app client ID |
| `client_secret` | The app client secret |
| `token_endpoint` | The OAuth token endpoint URL |
| `discovery_url` | The OpenID discovery URL |
| `created_at` | Timestamp of creation |
| `region` | AWS region |

## Usage

### 1. Obtain Access Token

Use the client credentials flow to get an access token:

```bash
curl -X POST https://member-liability-gateway.auth.us-east-1.amazoncognito.com/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials' \
  -d 'client_id=YOUR_CLIENT_ID' \
  -d 'client_secret=YOUR_CLIENT_SECRET' \
  -d 'scope=member-liability-api/read member-liability-api/write'
```

Response:
```json
{
  "access_token": "eyJraWQiOiJ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### 2. Use Access Token in API Requests

Include the access token in the Authorization header:

```bash
curl -X GET https://your-api-gateway.com/endpoint \
  -H 'Authorization: Bearer eyJraWQiOiJ...'
```

### 3. Python Example

```python
import requests
import base64
import json

# Load configuration
with open('cognito_config.json') as f:
    config = json.load(f)

# Encode credentials
credentials = base64.b64encode(
    f"{config['client_id']}:{config['client_secret']}".encode()
).decode()

# Request token
response = requests.post(
    config['token_endpoint'],
    headers={'Authorization': f'Basic {credentials}'},
    data={
        'grant_type': 'client_credentials',
        'scope': 'member-liability-api/read member-liability-api/write'
    }
)

access_token = response.json()['access_token']

# Use token in API calls
api_response = requests.get(
    'https://your-api.com/endpoint',
    headers={'Authorization': f'Bearer {access_token}'}
)
```

## API Gateway Integration

### Configure Cognito Authorizer

1. Open API Gateway console
2. Select your API
3. Go to "Authorizers"
4. Click "Create New Authorizer"
5. Configure:
   - **Name**: `CognitoAuthorizer`
   - **Type**: Cognito
   - **Cognito User Pool**: Select your user pool
   - **Token Source**: `Authorization`
   - **Token Validation**: Automatic

### Attach to API Methods

1. Select an API method (GET, POST, etc.)
2. Go to "Method Request"
3. Set **Authorization** to your Cognito authorizer
4. Set **OAuth Scopes** (optional):
   - `member-liability-api/read`
   - `member-liability-api/write`

## Security Considerations

### Token Security
- **Never commit** `cognito_config.json` to version control
- Store client secret in AWS Secrets Manager or environment variables
- Rotate client secrets regularly

### Access Control
- Use scopes to implement fine-grained access control
- Validate scopes in your backend API
- Log all authentication attempts

### Production Hardening
- Enable Advanced Security Mode in User Pool
- Set up CloudWatch alarms for failed authentication attempts
- Implement rate limiting in API Gateway
- Use AWS WAF for additional protection

## Troubleshooting

### Token Generation Fails

**Problem**: `curl` returns 400 Bad Request

**Solutions**:
1. Verify client ID and secret are correct
2. Check that scopes match exactly (including resource server identifier)
3. Ensure domain prefix is correct
4. Verify Content-Type header is set

### API Gateway Returns 401 Unauthorized

**Problem**: Valid token rejected by API Gateway

**Solutions**:
1. Verify Cognito authorizer is configured correctly
2. Check that User Pool ID matches
3. Ensure token is not expired (60 minute validity)
4. Verify Authorization header format: `Bearer <token>`

### Domain Prefix Already Exists

**Problem**: `create_user_pool_domain()` fails with InvalidParameterException

**Solutions**:
1. Domain prefixes must be globally unique across all AWS accounts
2. Add a timestamp or random string to make it unique
3. Update `DOMAIN_PREFIX` in the script

## Scripts

### Production Script: `08_create_cognito.py`
- Creates actual AWS resources
- Requires AWS credentials
- Saves to `cognito_config.json`

### Dry-Run Script: `08_create_cognito_dryrun.py`
- Simulates AWS API calls
- No credentials required
- Saves to `cognito_config_dryrun.json`

## Next Steps

1. **Configure API Gateway**: Add Cognito authorizer to your API
2. **Test Token Generation**: Use curl command to verify token generation
3. **Update Bedrock Agent**: Configure agent to use access token
4. **Test End-to-End**: Verify complete authentication flow
5. **Production Hardening**: Enable advanced security features

## References

- [AWS Cognito User Pools Documentation](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)
- [OAuth 2.0 Client Credentials Flow](https://oauth.net/2/grant-types/client-credentials/)
- [API Gateway Cognito Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html)
