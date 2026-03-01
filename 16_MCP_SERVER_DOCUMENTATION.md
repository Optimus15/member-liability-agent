# Member Benefits & Liability MCP Server Documentation

## Overview

This MCP (Model Context Protocol) server provides AI assistants with access to member eligibility, benefits, and liability APIs through the API Gateway. It enables seamless integration with healthcare systems for real-time data access.

## Architecture

```
┌─────────────────────┐
│   AI Assistant      │
│   (Claude, etc.)    │
└──────────┬──────────┘
           │ MCP Protocol
           ▼
┌─────────────────────┐
│   MCP Server        │
│   (This Server)     │
└──────────┬──────────┘
           │ HTTPS + OAuth
           ▼
┌─────────────────────┐
│   Cognito Auth      │
│   (Token Manager)   │
└──────────┬──────────┘
           │ Bearer Token
           ▼
┌─────────────────────┐
│   API Gateway       │
│   (AWS)             │
└──────────┬──────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│ Eligibility API  │  │ Liability API    │
│ (Lambda)         │  │ (Lambda)         │
└──────────────────┘  └──────────────────┘
```

## Features

### 1. Member Eligibility API
- Check member eligibility for benefits
- Verify enrollment status
- Get coverage period information
- Retrieve applicable policy rules

### 2. Member Benefits API
- Get detailed benefits information
- View coverage limits
- Check copays and deductibles
- Review out-of-pocket maximums

### 3. Member Liability API
- Calculate member liability for claims
- Get breakdown of costs (deductible, copay, coinsurance)
- Track out-of-pocket maximum
- View calculation audit trail

### 4. Order Lookup API
- Look up order information
- Get order status and details

### 5. Authentication
- Automatic Cognito OAuth token management
- Token caching and refresh
- Secure credential handling

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Required packages**:
   ```bash
   pip install mcp httpx
   ```

3. **API Gateway configured** (from previous scripts)
4. **Cognito authentication configured** (from script 08)

### Install MCP SDK

```bash
pip install mcp
```

### Install HTTP Client

```bash
pip install httpx
```

## Configuration

### Method 1: MCP Configuration File

Add to your `mcp.json` (typically in `~/.kiro/settings/mcp.json` or `.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "member-benefits-liability": {
      "command": "python3",
      "args": [
        "/absolute/path/to/01_member_liability_agent/16_member_benefits_liability_mcpserver.py"
      ],
      "env": {
        "GATEWAY_API_URL": "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod",
        "COGNITO_TOKEN_ENDPOINT": "https://your-domain.auth.us-east-1.amazoncognito.com/oauth2/token",
        "COGNITO_CLIENT_ID": "your-client-id",
        "COGNITO_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Method 2: Environment Variables

Set environment variables before running:

```bash
export GATEWAY_API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
export COGNITO_TOKEN_ENDPOINT="https://your-domain.auth.us-east-1.amazoncognito.com/oauth2/token"
export COGNITO_CLIENT_ID="your-client-id"
export COGNITO_CLIENT_SECRET="your-client-secret"

python3 16_member_benefits_liability_mcpserver.py
```

### Getting Configuration Values

#### 1. Gateway API URL

From `gateway_config.json`:
```bash
cat gateway_config.json | grep api_url
```

#### 2. Cognito Configuration

From `cognito_config.json`:
```bash
cat cognito_config.json | grep -E "(token_endpoint|client_id|client_secret)"
```

## Available Tools

### 1. check_member_eligibility

Check if a member is eligible for benefits on a specific service date.

**Parameters:**
- `member_id` (required): Unique member identifier (e.g., "M123456")
- `service_date` (required): Date of service in YYYY-MM-DD format (e.g., "2024-03-15")
- `benefit_code` (optional): Specific benefit code to check

**Returns:**
```json
{
  "isEligible": true,
  "enrollmentStatus": "ACTIVE",
  "coveragePeriod": {
    "startDate": "2024-01-01",
    "endDate": "2024-12-31"
  },
  "applicablePolicyRules": [...],
  "ineligibilityReason": null,
  "reasonCode": null
}
```

**Example Usage:**
```
Check eligibility for member M123456 on 2024-03-15
```

### 2. get_member_benefits

Get detailed benefits information for a member.

**Parameters:**
- `member_id` (required): Unique member identifier
- `benefit_type` (optional): Filter by benefit type (medical, dental, vision)

**Returns:**
```json
{
  "memberId": "M123456",
  "benefits": [
    {
      "benefitType": "medical",
      "coverageLimit": 1000000,
      "deductible": 1500,
      "copay": 25,
      "coinsurance": 0.2,
      "outOfPocketMax": 6000
    }
  ]
}
```

**Example Usage:**
```
Get benefits for member M123456
```

### 3. calculate_member_liability

Calculate member liability for a claim.

**Parameters:**
- `member_id` (required): Unique member identifier
- `claim_id` (required): Unique claim identifier (e.g., "CLM789012")
- `service_code` (optional): Service code (e.g., CPT code)
- `total_charges` (optional): Total charges amount in dollars

**Returns:**
```json
{
  "totalLiability": 350.00,
  "breakdown": {
    "deductibleAmount": 200.00,
    "copayAmount": 25.00,
    "coinsuranceAmount": 125.00,
    "outOfPocketApplied": 350.00,
    "remainingDeductible": 1300.00,
    "remainingOutOfPocket": 5650.00
  },
  "calculationSteps": [...],
  "appliedRules": [...]
}
```

**Example Usage:**
```
Calculate liability for member M123456 claim CLM789012
```

### 4. lookup_order

Look up order information and details.

**Parameters:**
- `order_id` (required): Unique order identifier

**Returns:**
```json
{
  "order_id": "ORD12345",
  "status": "completed",
  "details": {
    "created_date": "2024-03-15",
    "items": [...]
  }
}
```

**Example Usage:**
```
Look up order ORD12345
```

## Usage Examples

### Example 1: Check Eligibility

**User Query:**
```
Is member M123456 eligible for benefits on March 15, 2024?
```

**MCP Tool Call:**
```json
{
  "tool": "check_member_eligibility",
  "arguments": {
    "member_id": "M123456",
    "service_date": "2024-03-15"
  }
}
```

### Example 2: Get Benefits and Calculate Liability

**User Query:**
```
What are the benefits for member M123456 and how much would they owe for a $500 claim?
```

**MCP Tool Calls:**
```json
[
  {
    "tool": "get_member_benefits",
    "arguments": {
      "member_id": "M123456"
    }
  },
  {
    "tool": "calculate_member_liability",
    "arguments": {
      "member_id": "M123456",
      "claim_id": "CLM789012",
      "total_charges": 500.00
    }
  }
]
```

### Example 3: Complete Workflow

**User Query:**
```
Check if member M123456 is eligible, get their benefits, and calculate liability for a $750 medical claim on March 15, 2024
```

**MCP Tool Calls:**
```json
[
  {
    "tool": "check_member_eligibility",
    "arguments": {
      "member_id": "M123456",
      "service_date": "2024-03-15"
    }
  },
  {
    "tool": "get_member_benefits",
    "arguments": {
      "member_id": "M123456",
      "benefit_type": "medical"
    }
  },
  {
    "tool": "calculate_member_liability",
    "arguments": {
      "member_id": "M123456",
      "claim_id": "CLM789012",
      "service_code": "99213",
      "total_charges": 750.00
    }
  }
]
```

## Authentication Flow

### 1. Token Request

The MCP server automatically requests an OAuth token from Cognito:

```
POST https://your-domain.auth.us-east-1.amazoncognito.com/oauth2/token
Authorization: Basic <base64(client_id:client_secret)>
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&scope=member-liability-api/read member-liability-api/write
```

### 2. Token Caching

- Tokens are cached in memory
- Automatically refreshed 5 minutes before expiration
- No manual token management required

### 3. API Requests

All API requests include the Bearer token:

```
POST https://api-gateway-url/check-eligibility
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "memberId": "M123456",
  "serviceDate": "2024-03-15"
}
```

## Error Handling

### Authentication Errors

**Error**: `Failed to get access token`

**Solutions**:
1. Verify Cognito credentials are correct
2. Check token endpoint URL
3. Ensure client has correct permissions

### API Errors

**Error**: `API request failed with status 401`

**Solutions**:
1. Token may be expired (should auto-refresh)
2. Check API Gateway authorizer configuration
3. Verify Cognito User Pool is active

**Error**: `API request failed with status 404`

**Solutions**:
1. Verify API Gateway URL is correct
2. Check that endpoints are deployed
3. Ensure stage name is correct (usually "prod")

### Configuration Errors

**Error**: `GATEWAY_API_URL environment variable not set`

**Solutions**:
1. Set environment variable
2. Update MCP configuration file
3. Check configuration file path

## Testing

### Test MCP Server Locally

```bash
# Set environment variables
export GATEWAY_API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
export COGNITO_TOKEN_ENDPOINT="https://your-domain.auth.us-east-1.amazoncognito.com/oauth2/token"
export COGNITO_CLIENT_ID="your-client-id"
export COGNITO_CLIENT_SECRET="your-client-secret"

# Run server
python3 16_member_benefits_liability_mcpserver.py
```

### Test with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python3 16_member_benefits_liability_mcpserver.py
```

### Test Individual Tools

Use the MCP Inspector UI to test each tool with sample data.

## Security Considerations

### 1. Credential Storage

- **Never commit credentials to version control**
- Store in environment variables or secure configuration
- Use AWS Secrets Manager for production

### 2. Token Security

- Tokens are cached in memory only
- Automatically expire and refresh
- Not persisted to disk

### 3. API Access

- All requests use HTTPS
- Bearer token authentication
- API Gateway rate limiting applies

### 4. Least Privilege

- Use minimal OAuth scopes required
- Restrict API Gateway access
- Monitor CloudWatch logs

## Monitoring

### CloudWatch Logs

Monitor API Gateway and Lambda logs:
```bash
aws logs tail /aws/apigateway/your-api-id --follow
aws logs tail /aws/lambda/member-liability-check-eligibility --follow
```

### MCP Server Logs

The server logs to stderr:
- Authentication events
- API requests
- Errors and warnings

## Troubleshooting

### Server Won't Start

1. Check Python version: `python3 --version` (need 3.8+)
2. Verify MCP SDK installed: `pip show mcp`
3. Check environment variables are set
4. Review error messages in stderr

### Tools Not Appearing

1. Verify MCP configuration file syntax
2. Check server is running
3. Restart AI assistant
4. Review MCP server logs

### API Calls Failing

1. Test API Gateway directly with curl
2. Verify Cognito token generation
3. Check Lambda function logs
4. Ensure API is deployed

## Integration with AI Assistants

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "member-benefits-liability": {
      "command": "python3",
      "args": ["/path/to/16_member_benefits_liability_mcpserver.py"],
      "env": {
        "GATEWAY_API_URL": "...",
        "COGNITO_TOKEN_ENDPOINT": "...",
        "COGNITO_CLIENT_ID": "...",
        "COGNITO_CLIENT_SECRET": "..."
      }
    }
  }
}
```

### Kiro IDE

Add to `.kiro/settings/mcp.json` or `~/.kiro/settings/mcp.json`

## Next Steps

1. ✅ MCP server created
2. ⏳ **Configure environment variables**
3. ⏳ **Test server locally**
4. ⏳ **Add to MCP configuration**
5. ⏳ **Test with AI assistant**
6. ⏳ **Monitor and optimize**

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review MCP server stderr output
3. Test API Gateway endpoints directly
4. Verify Cognito authentication

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS Cognito OAuth 2.0](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-userpools-server-contract-reference.html)
