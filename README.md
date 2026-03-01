# Member Liability Agent - AWS Bedrock Implementation

AWS Bedrock Agent implementation for the Benefits and Member Liability, MCP server with tools (Member Eligibility, Member Benefits and Member Liability), memory management, and API Gateway setup.

## Overview

This project contains Python scripts to deploy and configure an AWS Bedrock Agent that handles member benefits eligibility verification and liability calculations. The agent integrates with AWS services.

## Features

- ✅ **AWS Bedrock Agent** with Claude 3 Sonnet model
- ✅ **Custom Lambda Tools** for eligibility, Benefits and liability calculations
- ✅ **Agent Memory** with session summary, user preferences, and semantic memory
- ✅ **Cognito Authentication** for secure API access
- ✅ **API Gateway** with OAuth integration
- ✅ **MCP Server** for AI assistant integration
- ✅ **Comprehensive Documentation** for all components

## Project Structure

```
01_member_liability_agent/
├── create_agent.py                    # Main agent creation script
├── lambda_check_eligibility.py        # Lambda: Check member eligibility
├── lambda_calculate_liability.py      # Lambda: Calculate member liability
├── deploy.sh                          # Lambda deployment script
├── 02_test_agent.py                   # Agent workflow testing
├── 02_test_agent_dryrun.py           # Dry-run testing (no AWS)
├── 03_create_memory.py                # Memory setup script
├── 03_create_memory_dryrun.py        # Memory dry-run
├── 04_seed_memory.py                  # Seed memory with conversations
├── 04_seed_memory_dryrun.py          # Memory seeding dry-run
├── 05_test_memory.py                  # Test memory retrieval
├── 05_test_memory_dryrun.py          # Memory testing dry-run
├── 08_create_cognito.py               # Cognito authentication setup
├── 08_create_cognito_dryrun.py       # Cognito dry-run
├── 11_create_gateway.py               # API Gateway creation
├── 11_create_gateway_dryrun.py       # Gateway dry-run
├── 12_add_lambda_to_gateway.py       # Lambda-Gateway integration
├── 12_add_lambda_to_gateway_dryrun.py # Integration dry-run
├── 14_full_agent.py                   # Full-featured agent with all integrations
├── 15_test_full_agent.py              # Test full agent functionality
├── 16_member_benefits_liability_mcpserver.py # MCP server for AI assistants
├── README.md                          # This file
├── ARCHITECTURE.md                    # Architecture documentation
└── *.json                             # Configuration files (generated)
```

## Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- boto3 installed: `pip install boto3`

### Installation

```bash
# Clone the repository
git clone https://github.com/Optimus15/member-liability-agent.git
cd member-liability-agent

# Install dependencies
pip install boto3 uuid

# Configure AWS credentials
aws configure
```

### Basic Usage

#### 1. Create the Bedrock Agent

```bash
python create_agent.py
```

This creates:
- Bedrock Agent with Claude 3 Sonnet
- Custom Lambda function tools
- IAM roles and permissions

Configuration saved to: `agent_config.json`, `kb_config.json`

#### 2. Test the Agent

```bash
# Dry-run (no AWS credentials needed)
python 02_test_agent_dryrun.py

# Production test
python 02_test_agent.py
```

Tests a 4-step workflow:
1. Check member eligibility
2. Verify member has benefits
3. Calculate liability

#### 3. Set Up Agent Memory

```bash
# Dry-run
python 03_create_memory_dryrun.py

# Production
python 03_create_memory.py
```

Creates memory with three strategies:
- Session summary
- User preferences
- Semantic memory

#### 4. Seed Memory with Sample Data

```bash
# Dry-run
python 04_seed_memory_dryrun.py

# Production
python 04_seed_memory.py
```

Adds sample conversations for testing memory recall.

#### 5. Test Memory Retrieval

```bash
# Dry-run
python 05_test_memory_dryrun.py

# Production
python 05_test_memory.py
```

Retrieves and displays agent memory for a user.

## Advanced Setup

### Cognito Authentication

```bash
# Dry-run
python 08_create_cognito_dryrun.py

# Production
python 08_create_cognito.py
```

Sets up:
- Cognito User Pool
- OAuth domain and endpoints
- App client for machine-to-machine auth
- Resource server with scopes

Configuration saved to: `cognito_config.json`

### API Gateway

```bash
# Dry-run
python 11_create_gateway_dryrun.py

# Production
python 11_create_gateway.py
```

Creates:
- REST API Gateway
- Cognito authorizer
- API endpoints

Configuration saved to: `gateway_config.json`

### Lambda-Gateway Integration

```bash
# Dry-run
python 12_add_lambda_to_gateway_dryrun.py

# Production
python 12_add_lambda_to_gateway.py
```

Integrates Lambda functions with API Gateway:
- Creates resources and methods
- Configures Lambda permissions
- Deploys to production stage

### Full-Featured Agent

```bash
python 14_full_agent.py
```

Creates a complete agent with:
- Memory integration
- Gateway integration
- Knowledge Base
- All Lambda tools

### Test Full Agent

```bash
python 15_test_full_agent.py
```

Comprehensive testing:
- Memory recall verification
- Eligibility lookup
- Personalized responses

## MCP Server

The MCP server allows AI assistants to interact with the member liability APIs.

### Setup

```bash
# Install dependencies
pip install mcp httpx

# Set environment variables
export COGNITO_DOMAIN_PREFIX="your-domain-prefix"
export COGNITO_CLIENT_ID="your-client-id"
export COGNITO_CLIENT_SECRET="your-client-secret"
export API_GATEWAY_URL="https://your-api.execute-api.region.amazonaws.com/prod"

# Run the MCP server
python 16_member_benefits_liability_mcpserver.py
```

### MCP Tools Available

1. **check_member_eligibility** - Verify member eligibility
2. **get_member_benefits** - Retrieve member benefits
3. **calculate_member_liability** - Calculate liability amounts

## Configuration Files

All scripts generate JSON configuration files:

- `agent_config.json` - Agent ID and details
- `kb_config.json` - Knowledge Base configuration
- `memory_config.json` - Memory ID and settings
- `cognito_config.json` - Cognito authentication details
- `gateway_config.json` - API Gateway configuration
- `lambda_config.json` - Lambda function ARNs
- `lambda_integration_config.json` - Integration details
- `full_agent_config.json` - Complete agent configuration

**⚠️ Important**: Add `*_config.json` to `.gitignore` to avoid committing credentials.

## Dry-Run Scripts

Every production script has a corresponding dry-run version that:
- Simulates API calls without AWS credentials
- Generates sample configuration files
- Validates script logic
- Useful for testing and development

Dry-run files are suffixed with `_dryrun.py`.

## Documentation

Comprehensive documentation is available:

- **README.md** (this file) - Quick start and overview
- **ARCHITECTURE.md** - Detailed architecture documentation
- **Individual script documentation** - Each script has detailed comments

### Documentation Files

- `02_TEST_DOCUMENTATION.md` - Agent testing guide
- `03_MEMORY_DOCUMENTATION.md` - Memory setup guide
- `03_API_VALIDATION.md` - API validation details
- `04_SEED_MEMORY_DOCUMENTATION.md` - Memory seeding guide
- `05_TEST_MEMORY_SUMMARY.md` - Memory testing guide
- `08_COGNITO_DOCUMENTATION.md` - Cognito setup guide
- `11_GATEWAY_DOCUMENTATION.md` - API Gateway guide
- `12_LAMBDA_INTEGRATION_SUMMARY.md` - Lambda integration guide
- `16_MCP_SERVER_DOCUMENTATION.md` - MCP server guide

### Execution Summaries

- `TEST_EXECUTION_SUMMARY.md` - Test execution results
- `03_MEMORY_SETUP_SUMMARY.md` - Memory setup results
- `MEMORY_EXECUTION_SUMMARY.md` - Memory execution results
- `SEED_MEMORY_EXECUTION_SUMMARY.md` - Seeding results
- `08_COGNITO_EXECUTION_SUMMARY.md` - Cognito setup results
- `11_GATEWAY_EXECUTION_SUMMARY.md` - Gateway creation results
- `15_TEST_EXECUTION_RESULTS.md` - Full agent test results

## AWS Services Used

- **Amazon Bedrock** - Foundation model (Claude 3 Sonnet)
- **AWS Lambda** - Custom function tools
- **Amazon Cognito** - Authentication and authorization
- **API Gateway** - REST API endpoints
- **IAM** - Roles and permissions
- **CloudFormation** - Infrastructure (for Knowledge Base)

## Security Considerations

- All credentials stored in configuration files (not in code)
- Cognito OAuth for API authentication
- IAM roles with least privilege
- API Gateway with Cognito authorizer
- Configuration files excluded from version control

## Troubleshooting

### Common Issues

**Issue**: AWS credentials not configured
```bash
# Solution
aws configure
```

**Issue**: Permission denied errors
```bash
# Solution: Ensure IAM user has required permissions
# - bedrock:*
# - lambda:*
# - cognito-idp:*
# - apigateway:*
# - iam:CreateRole, iam:AttachRolePolicy
```

**Issue**: Knowledge Base not found
```bash
# Solution: Create Knowledge Base first or update kb_config.json
```

**Issue**: Lambda deployment fails
```bash
# Solution: Check deploy.sh has execute permissions
chmod +x deploy.sh
```

## Development Workflow

1. **Test with dry-run scripts** - Validate logic without AWS
2. **Run production scripts** - Deploy to AWS
3. **Verify configuration files** - Check generated JSON files
4. **Test functionality** - Use test scripts
5. **Monitor AWS Console** - Verify resources created

## Cost Considerations

AWS services used incur costs:
- Bedrock Agent invocations
- Lambda function executions
- API Gateway requests
- Cognito user pool (free tier available)

Estimate costs using AWS Pricing Calculator.

## Related Projects

- **TypeScript Implementation** - Core business logic and calculations
- **Kiro Specs** - Requirements, design, and implementation tasks

## Contributing

1. Test changes with dry-run scripts first
2. Update documentation for new features
3. Follow existing code patterns
4. Add error handling and logging

## License

MIT

## Support

For issues or questions:
1. Check documentation files
2. Review execution summary files
3. Check AWS CloudWatch logs
4. Open an issue on GitHub

## Acknowledgments

Built with:
- AWS Bedrock for foundation models
- boto3 for AWS SDK
- Python 3 for scripting
- MCP for AI assistant integration

---

**Version**: 1.0.0  
**Last Updated**: March 15, 2024  
**AWS Region**: Configurable (default: us-east-1)
