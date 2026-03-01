# Design Specification: AWS Bedrock Member Liability Agent

## Document Information

**Version**: 1.0.0  
**Last Updated**: March 15, 2024  
**Status**: Implementation Complete  
**Author**: AWS Bedrock Implementation Team

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Design](#component-design)
4. [Data Models](#data-models)
5. [API Specifications](#api-specifications)
6. [Security Design](#security-design)
7. [Integration Patterns](#integration-patterns)
8. [Deployment Architecture](#deployment-architecture)
9. [Testing Strategy](#testing-strategy)
10. [Performance Considerations](#performance-considerations)

## Overview

### Purpose

The AWS Bedrock Member Liability Agent is an intelligent conversational AI system designed to automate member benefits eligibility verification and liability calculations for healthcare insurance systems. The agent leverages AWS Bedrock's foundation models (Claude 3 Sonnet) combined with custom Lambda function tools, Knowledge Base integration, and memory capabilities to provide accurate, context-aware responses.

### Design Goals

1. **Intelligent Automation**: Automate complex eligibility and liability calculations using AI
2. **Contextual Memory**: Remember user preferences and conversation history
3. **Knowledge Integration**: Access policy documents and benefit information via Knowledge Base
4. **Secure Access**: Implement OAuth-based authentication for API access
5. **Scalability**: Support high-volume concurrent requests
6. **Auditability**: Maintain complete audit trails for compliance
7. **Extensibility**: Easy addition of new tools and capabilities

### Key Features

- AWS Bedrock Agent with Claude 3 Sonnet foundation model
- Custom Lambda function tools for business logic
- Agent memory with three strategies (session, preferences, semantic)
- Cognito-based OAuth authentication
- API Gateway for external access
- MCP server for AI assistant integration


## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web App    │  │  Mobile App  │  │ AI Assistant │          │
│  │              │  │              │  │   (MCP)      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    API Gateway Layer                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Amazon API Gateway (REST API)                             │  │
│  │  - Cognito Authorizer                                      │  │
│  │  - Request/Response Transformation                         │  │
│  │  - Rate Limiting & Throttling                              │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                  Authentication Layer                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Amazon Cognito                                            │  │
│  │  - User Pool                                               │  │
│  │  - OAuth 2.0 / OpenID Connect                             │  │
│  │  - Client Credentials Flow                                │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                    Bedrock Agent Layer                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  AWS Bedrock Agent                                         │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │  Foundation Model: Claude 3 Sonnet                   │ │  │
│  │  │  - Natural language understanding                    │ │  │
│  │  │  - Context management                                │ │  │
│  │  │  - Response generation                               │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │  Agent Memory                                        │ │  │
│  │  │  - Session Summary                                   │ │  │
│  │  │  - User Preferences                                  │ │  │
│  │  │  - Semantic Memory                                   │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────┬────────────────────────┬──────────────────────────────────┘
        │                        │
        │                        │
┌───────▼────────┐      ┌────────▼──────────┐
│  Knowledge     │      │  Action Groups    │
│  Base          │      │  (Lambda Tools)   │
│                │      │                   │
│                │      │  ┌─────────────┐  │
│  - Benefits    │      │  │ Eligibility │  │
│  - Procedures  │      │  │   Check     │  │
│  - FAQs        │      │  └─────────────┘  │
│                │      │  ┌─────────────┐  │
│                │      │  │ Liability   │  │
│                │      │  │ Calculate   │  │
│                │      │  └─────────────┘  │
│                │      │  ┌─────────────┐  │
│                │      │  │   Benefit   │  │
│                │      │  │   Lookup    │  │
│                │      │  └─────────────┘  │
└────────────────┘      └───────────────────┘
```

### Component Interaction Flow

```
User Request Flow:
1. Client → API Gateway (with OAuth token)
2. API Gateway → Cognito (validate token)
3. API Gateway → Bedrock Agent (invoke)
4. Bedrock Agent → Claude 3 Sonnet (process request)
5. Claude 3 Sonnet → Knowledge Base (retrieve context)
6. Claude 3 Sonnet → Lambda Tools (execute actions)
7. Bedrock Agent → Memory (store/retrieve context)
8. Bedrock Agent → API Gateway (response)
9. API Gateway → Client (formatted response)
```


## Component Design

### 1. AWS Bedrock Agent

**Purpose**: Core conversational AI component that orchestrates all interactions.

**Configuration**:
- **Foundation Model**: Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
- **Agent Name**: `benefits-member-liability-agent`
- **Instruction**: System prompt defining agent behavior and capabilities
- **Idle Session TTL**: 600 seconds (10 minutes)

**Capabilities**:
- Natural language understanding and generation
- Context management across conversations
- Tool invocation based on user intent
- Knowledge Base querying
- Memory storage and retrieval

**System Prompt**:
```
You are a helpful benefits and member liability assistant. You help members understand their 
benefits eligibility and calculate their liability amounts. You have access to:

1. A knowledge base with policy documents and benefit information
2. Tools to check member eligibility
3. Tools to calculate member liability


Always be helpful, accurate, and professional. When calculating liability or checking 
eligibility, use the appropriate tools. When answering general questions about benefits, 
search the knowledge base first.
```

### 2. Knowledge Base Integration

**Purpose**: Provide the agent with access to policy documents, benefit information, and FAQs.

**Design**:
- **Type**: AWS Bedrock Knowledge Base
- **Retrieval**: Semantic search using embeddings
- **Integration**: Automatic retrieval during agent invocation
- **Configuration**: Retrieved from CloudFormation stack or manual configuration

**Document Types**:
- Policy documents (PDF, DOCX)
- Benefit summaries (TXT, MD)
- Procedure guides (PDF)
- FAQs (MD, HTML)
- Coverage details (JSON, CSV)

**Retrieval Strategy**:
- Semantic similarity search
- Top-k results (configurable, default: 5)
- Relevance threshold filtering
- Context window management

### 3. Lambda Function Tools (Action Groups)

**Purpose**: Execute business logic for eligibility checks and liability calculations.

#### 3.1 Check Eligibility Tool

**Lambda Function**: `lambda_check_eligibility.py`

**API Schema**:
```json
{
  "name": "check_eligibility",
  "description": "Check if a member is eligible for benefits on a specific service date",
  "parameters": {
    "member_id": {
      "type": "string",
      "description": "The unique identifier for the member",
      "required": true
    },
    "service_date": {
      "type": "string",
      "description": "The date of service in YYYY-MM-DD format",
      "required": true
    },
    "benefit_code": {
      "type": "string",
      "description": "Optional benefit code to check specific benefit eligibility",
      "required": false
    }
  }
}
```

**Response Format**:
```json
{
  "is_eligible": true,
  "member_id": "M001",
  "enrollment_status": "ACTIVE",
  "coverage_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "plan_id": "PLAN001",
  "plan_type": "PPO",
  "message": "Member is eligible for benefits"
}
```

#### 3.2 Calculate Liability Tool

**Lambda Function**: `lambda_calculate_liability.py`

**API Schema**:
```json
{
  "name": "calculate_member_liability",
  "description": "Calculate the member's liability amount for a claim",
  "parameters": {
    "member_id": {
      "type": "string",
      "description": "The unique identifier for the member",
      "required": true
    },
    "service_code": {
      "type": "string",
      "description": "The service code for the claim",
      "required": true
    },
    "total_charges": {
      "type": "number",
      "description": "The total charges for the service in dollars",
      "required": true
    },
    "service_date": {
      "type": "string",
      "description": "The date of service in YYYY-MM-DD format",
      "required": true
    }
  }
}
```

**Response Format**:
```json
{
  "total_liability": 250.00,
  "breakdown": {
    "deductible": 100.00,
    "copay": 50.00,
    "coinsurance": 100.00,
    "out_of_pocket_applied": 0.00
  },
  "remaining_deductible": 900.00,
  "remaining_out_of_pocket": 4750.00,
  "message": "Liability calculated successfully"
}
```



### 4. Agent Memory

**Purpose**: Maintain conversation context and user preferences across sessions.

**Memory Strategies**:

#### 4.1 Session Summary
- **Type**: `SESSION_SUMMARY`
- **Purpose**: Summarize conversation history within a session
- **Retention**: Duration of session (10 minutes idle timeout)
- **Use Case**: Maintain context within a single conversation

#### 4.2 User Preferences
- **Type**: `USER_PREFERENCES`
- **Purpose**: Store user-specific preferences and settings
- **Retention**: 30 days
- **Use Case**: Remember communication preferences, frequently accessed information

#### 4.3 Semantic Memory
- **Type**: `SEMANTIC_MEMORY`
- **Purpose**: Store and retrieve semantically similar past interactions
- **Retention**: 30 days
- **Use Case**: Recall relevant past conversations and decisions

**Memory Configuration**:
```python
{
    "memoryName": "member_liability_memory",
    "memoryStrategies": [
        {
            "type": "SESSION_SUMMARY",
            "maxTokens": 2000
        },
        {
            "type": "USER_PREFERENCES",
            "maxTokens": 1000
        },
        {
            "type": "SEMANTIC_MEMORY",
            "maxTokens": 3000,
            "similarityThreshold": 0.7
        }
    ],
    "storageConfiguration": {
        "retentionDays": 30
    }
}
```

### 5. Authentication & Authorization

**Purpose**: Secure API access using OAuth 2.0 and Cognito.

**Components**:

#### 5.1 Cognito User Pool
- **Purpose**: Manage user authentication
- **Configuration**:
  - User pool name: `member-liability-user-pool`
  - Domain prefix: Configurable
  - OAuth flows: Client credentials
  - Token expiration: 1 hour

#### 5.2 Resource Server
- **Purpose**: Define API scopes
- **Scopes**:
  - `member-liability-api/read` - Read access to member data
  - `member-liability-api/write` - Write access for calculations

#### 5.3 App Client
- **Type**: Machine-to-machine (M2M)
- **Grant Type**: Client credentials
- **Authentication**: Client ID + Client Secret
- **Token Endpoint**: `https://{domain}.auth.{region}.amazoncognito.com/oauth2/token`

**Authentication Flow**:
```
1. Client requests token from Cognito
   POST /oauth2/token
   Headers: Authorization: Basic base64(client_id:client_secret)
   Body: grant_type=client_credentials&scope=member-liability-api/read

2. Cognito returns access token
   {
     "access_token": "eyJraWQ...",
     "token_type": "Bearer",
     "expires_in": 3600
   }

3. Client includes token in API requests
   GET /member-liability/eligibility
   Headers: Authorization: Bearer eyJraWQ...

4. API Gateway validates token with Cognito
5. Request forwarded to Bedrock Agent
```

### 6. API Gateway

**Purpose**: Provide RESTful API interface to the Bedrock Agent.

**Configuration**:
- **API Type**: REST API
- **Name**: `ReturnsRefundsGateway` (configurable)
- **Endpoint Type**: REGIONAL
- **Authorization**: Cognito User Pool Authorizer

**Resources & Methods**:

```
/member-liability
  POST - Invoke agent with user query
    - Request: { "query": "string", "sessionId": "string" }
    - Response: { "response": "string", "sessionId": "string" }

/eligibility
  POST - Check member eligibility
    - Request: { "member_id": "string", "service_date": "string" }
    - Response: Eligibility result

/liability
  POST - Calculate member liability
    - Request: { "member_id": "string", "service_code": "string", ... }
    - Response: Liability calculation

```

**Integration Type**: AWS_PROXY (Lambda proxy integration)

**Deployment**:
- **Stage**: prod
- **Throttling**: 10,000 requests per second
- **Burst**: 5,000 requests


### 7. MCP Server

**Purpose**: Enable AI assistants (like Claude Desktop, Cursor) to interact with the member liability APIs.

**Protocol**: Model Context Protocol (MCP)

**Implementation**: `16_member_benefits_liability_mcpserver.py`

**Features**:
- Automatic OAuth token management
- Token caching with refresh (5-minute buffer)
- Four MCP tools exposed
- Async HTTP requests using httpx

**MCP Tools**:

1. **check_member_eligibility**
   - Input: member_id, service_date, benefit_code (optional)
   - Output: Eligibility result

2. **get_member_benefits**
   - Input: member_id
   - Output: List of benefits

3. **calculate_member_liability**
   - Input: member_id, service_code, total_charges, service_date
   - Output: Liability calculation



**Configuration**:
```json
{
  "mcpServers": {
    "member-liability": {
      "command": "python",
      "args": ["16_member_benefits_liability_mcpserver.py"],
      "env": {
        "COGNITO_DOMAIN_PREFIX": "your-domain",
        "COGNITO_CLIENT_ID": "your-client-id",
        "COGNITO_CLIENT_SECRET": "your-secret",
        "API_GATEWAY_URL": "https://api.execute-api.region.amazonaws.com/prod"
      }
    }
  }
}
```

## Data Models

### Member

```python
{
    "member_id": "string",           # Unique member identifier
    "first_name": "string",          # Member first name
    "last_name": "string",           # Member last name
    "date_of_birth": "YYYY-MM-DD",   # Date of birth
    "enrollment_status": "enum",     # ACTIVE, INACTIVE, SUSPENDED, TERMINATED
    "plans": [                       # Array of member plans
        {
            "plan_id": "string",
            "plan_type": "enum",     # HMO, PPO, HIGH_DEDUCTIBLE, EPO
            "is_primary": boolean,
            "coverage_period": {
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD"
            },
            "deductible": number,    # In cents
            "out_of_pocket_maximum": number  # In cents
        }
    ]
}
```

### Claim

```python
{
    "claim_id": "string",            # Unique claim identifier
    "member_id": "string",           # Reference to member
    "service_date": "YYYY-MM-DD",    # Date of service
    "service_code": "string",        # CPT/HCPCS code
    "service_category": "string",    # Category (e.g., PRIMARY_CARE)
    "provider_id": "string",         # Provider identifier
    "total_charges": number,         # In cents
    "diagnosis_codes": ["string"],   # ICD-10 codes
    "prior_authorization_id": "string",  # Optional
    "submitted_date": "YYYY-MM-DD"   # Submission date
}
```

### Eligibility Result

```python
{
    "is_eligible": boolean,
    "member_id": "string",
    "service_date": "YYYY-MM-DD",
    "enrollment_status": "enum",
    "coverage_period": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD"
    },
    "plan_id": "string",
    "plan_type": "enum",
    "applicable_policy_rules": [     # Array of applicable rules
        {
            "rule_id": "string",
            "rule_name": "string",
            "priority": number
        }
    ],
    "ineligibility_reason": "string",  # If not eligible
    "reason_code": "string",           # Error code
    "message": "string"
}
```

### Liability Result

```python
{
    "total_liability": number,       # In cents
    "breakdown": {
        "deductible_amount": number,
        "copay_amount": number,
        "coinsurance_amount": number,
        "out_of_pocket_applied": number
    },
    "remaining_deductible": number,
    "remaining_out_of_pocket": number,
    "calculation_steps": [           # Audit trail
        {
            "step_number": number,
            "operation": "string",
            "input_values": {},
            "output_value": any,
            "applied_rule": "string",
            "timestamp": "ISO8601"
        }
    ],
    "applied_rules": [               # Rules used in calculation
        {
            "rule_id": "string",
            "rule_name": "string",
            "impact": "string"
        }
    ],
    "timestamp": "ISO8601",
    "message": "string"
}
```

### Agent Invocation Request

```python
{
    "sessionId": "string",           # Session identifier
    "inputText": "string",           # User query
    "enableTrace": boolean,          # Enable detailed tracing
    "endSession": boolean            # End session after response
}
```

### Agent Invocation Response

```python
{
    "completion": "string",          # Agent's response
    "sessionId": "string",           # Session identifier
    "trace": {                       # Detailed execution trace
        "orchestrationTrace": {},
        "knowledgeBaseTrace": {},
        "actionGroupTrace": {}
    },
    "memoryId": "string"            # Memory identifier
}
```


## API Specifications

### REST API Endpoints

#### 1. Invoke Agent

**Endpoint**: `POST /member-liability`

**Description**: Send a natural language query to the Bedrock Agent.

**Request**:
```json
{
  "query": "Can you check if member M001 is eligible for benefits?",
  "sessionId": "optional-session-id"
}
```

**Response**:
```json
{
  "response": "Let me check that for you. Member M001 is currently eligible for benefits...",
  "sessionId": "generated-or-provided-session-id",
  "timestamp": "2024-03-15T10:30:00Z"
}
```

**Status Codes**:
- 200: Success
- 400: Bad request (invalid input)
- 401: Unauthorized (invalid token)
- 500: Internal server error

#### 2. Check Eligibility

**Endpoint**: `POST /eligibility`

**Description**: Directly check member eligibility without conversational interface.

**Request**:
```json
{
  "member_id": "M001",
  "service_date": "2024-03-15",
  "benefit_code": "OFFICE_VISIT"
}
```

**Response**:
```json
{
  "is_eligible": true,
  "member_id": "M001",
  "enrollment_status": "ACTIVE",
  "coverage_period": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "plan_id": "PLAN001",
  "plan_type": "PPO",
  "message": "Member is eligible for benefits"
}
```

#### 3. Calculate Liability

**Endpoint**: `POST /liability`

**Description**: Calculate member liability for a service.

**Request**:
```json
{
  "member_id": "M001",
  "service_code": "99213",
  "total_charges": 200.00,
  "service_date": "2024-03-15"
}
```

**Response**:
```json
{
  "total_liability": 50.00,
  "breakdown": {
    "deductible": 0.00,
    "copay": 30.00,
    "coinsurance": 20.00,
    "out_of_pocket_applied": 0.00
  },
  "remaining_deductible": 1000.00,
  "remaining_out_of_pocket": 4950.00,
  "message": "Liability calculated successfully"
}
```

### Authentication Headers

All API requests must include:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "constraint": "validation_rule"
    },
    "timestamp": "2024-03-15T10:30:00Z",
    "request_id": "unique-request-id"
  }
}
```

### Rate Limiting

- **Requests per second**: 10,000
- **Burst capacity**: 5,000
- **Per-client limit**: 100 requests/second

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1710504600
```

## Security Design

### Authentication Flow

```
┌──────────┐                                    ┌──────────┐
│  Client  │                                    │ Cognito  │
└────┬─────┘                                    └────┬─────┘
     │                                                │
     │  1. Request Token (Client Credentials)        │
     │ ──────────────────────────────────────────>   │
     │                                                │
     │  2. Validate Client ID & Secret               │
     │                                                │
     │  3. Return Access Token                       │
     │ <──────────────────────────────────────────   │
     │                                                │
┌────▼─────┐                                    ┌────▼─────┐
│  Client  │                                    │   API    │
│ (w/token)│                                    │ Gateway  │
└────┬─────┘                                    └────┬─────┘
     │                                                │
     │  4. API Request + Bearer Token                │
     │ ──────────────────────────────────────────>   │
     │                                                │
     │  5. Validate Token with Cognito               │
     │                                                │
     │  6. Forward to Bedrock Agent                  │
     │                                                │
     │  7. Return Response                           │
     │ <──────────────────────────────────────────   │
     │                                                │
```

### IAM Roles and Permissions

#### Bedrock Agent Execution Role

**Purpose**: Allow Bedrock Agent to invoke Lambda functions and access Knowledge Base.

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:*:*:function:check_eligibility",
        "arn:aws:lambda:*:*:function:calculate_liability",
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:*:*:knowledge-base/*"
    }
  ]
}
```

#### Lambda Execution Role

**Purpose**: Allow Lambda functions to execute and access necessary resources.

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/members"
    }
  ]
}
```

#### API Gateway Invocation Role

**Purpose**: Allow API Gateway to invoke Bedrock Agent.

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock:*:*:agent/*"
    }
  ]
}
```

### Data Encryption

#### At Rest
- **Knowledge Base**: Encrypted using AWS KMS
- **Agent Memory**: Encrypted using AWS managed keys
- **Configuration Files**: Excluded from version control

#### In Transit
- **API Gateway**: HTTPS/TLS 1.2+
- **Lambda Invocations**: AWS internal encryption
- **Cognito**: HTTPS/TLS 1.2+

### Security Best Practices

1. **Credential Management**
   - Store credentials in AWS Secrets Manager
   - Rotate credentials regularly (90 days)
   - Never commit credentials to version control

2. **Access Control**
   - Principle of least privilege for IAM roles
   - Separate roles for different components
   - Regular access audits

3. **API Security**
   - OAuth 2.0 for authentication
   - Rate limiting to prevent abuse
   - Input validation on all endpoints
   - CORS configuration for web clients

4. **Monitoring**
   - CloudWatch logs for all components
   - CloudTrail for API calls
   - Alerts for suspicious activity
   - Regular security assessments


## Integration Patterns

### 1. Knowledge Base Integration Pattern

```python
# Agent automatically queries Knowledge Base when needed
# No explicit code required - configured in agent setup

# Knowledge Base Configuration
knowledge_base_config = {
    "knowledgeBaseId": "KB123456",
    "retrievalConfiguration": {
        "vectorSearchConfiguration": {
            "numberOfResults": 5,
            "overrideSearchType": "HYBRID"  # Semantic + keyword
        }
    }
}

# Agent uses KB for:
# - Policy document lookups
# - Benefit information queries
# - FAQ responses
# - Procedure guidelines
```

### 2. Lambda Tool Invocation Pattern

```python
# Agent invokes Lambda based on user intent
# Example: User asks "Is member M001 eligible?"

# 1. Agent identifies intent: check_eligibility
# 2. Agent extracts parameters: member_id="M001"
# 3. Agent invokes Lambda function
# 4. Lambda returns result
# 5. Agent incorporates result into response

# Lambda Response Format
{
    "statusCode": 200,
    "body": json.dumps({
        "is_eligible": True,
        "member_id": "M001",
        "message": "Member is eligible"
    })
}
```

### 3. Memory Integration Pattern

```python
# Memory is automatically managed by Bedrock Agent
# Stored per user/session

# Session Summary Example:
# "User asked about member M001's eligibility. 
#  Member was found to be eligible with PPO plan."

# User Preferences Example:
# "User prefers detailed breakdowns of liability calculations.
#  User typically asks about member M001."

# Semantic Memory Example:
# Previous conversation about similar eligibility question
# retrieved when relevant
```

### 4. API Gateway Integration Pattern

```python
# API Gateway → Lambda → Bedrock Agent

# API Gateway Request Transformation
{
    "body": {
        "query": "$input.json('$.query')",
        "sessionId": "$input.json('$.sessionId')"
    },
    "headers": {
        "Authorization": "$input.params('Authorization')"
    }
}

# Lambda Integration (AWS_PROXY)
def lambda_handler(event, context):
    # Extract request
    body = json.loads(event['body'])
    query = body['query']
    session_id = body.get('sessionId')
    
    # Invoke Bedrock Agent
    response = bedrock_agent_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=alias_id,
        sessionId=session_id,
        inputText=query
    )
    
    # Return response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': response['completion'],
            'sessionId': response['sessionId']
        })
    }
```

### 5. MCP Server Integration Pattern

```python
# MCP Server acts as bridge between AI assistants and APIs

# Token Management
class TokenManager:
    def __init__(self):
        self.token = None
        self.expires_at = None
    
    async def get_token(self):
        # Check if token is valid
        if self.token and self.expires_at > time.time() + 300:
            return self.token
        
        # Request new token
        response = await httpx.post(
            f"{cognito_domain}/oauth2/token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"}
        )
        
        self.token = response.json()['access_token']
        self.expires_at = time.time() + response.json()['expires_in']
        return self.token

# MCP Tool Implementation
@server.call_tool()
async def check_eligibility(member_id: str, service_date: str):
    token = await token_manager.get_token()
    
    response = await httpx.post(
        f"{api_url}/eligibility",
        headers={"Authorization": f"Bearer {token}"},
        json={"member_id": member_id, "service_date": service_date}
    )
    
    return response.json()
```

## Deployment Architecture

### AWS Resources

```
Region: us-east-1 (configurable)

├── Amazon Bedrock
│   ├── Agent: benefits-member-liability-agent
│   ├── Agent Alias: PROD
│   ├── Knowledge Base: (from CloudFormation)
│   └── Memory: member_liability_memory
│
├── AWS Lambda
│   ├── Function: check_eligibility
│   ├── Function: calculate_liability
│   └── Function: benefit_lookup
│
├── Amazon Cognito
│   ├── User Pool: member-liability-user-pool
│   ├── Domain: {prefix}.auth.{region}.amazoncognito.com
│   ├── Resource Server: member-liability-api
│   └── App Client: member-liability-client
│
├── Amazon API Gateway
│   ├── API: ReturnsRefundsGateway
│   ├── Authorizer: Cognito User Pool
│   ├── Resources: /member-liability, /eligibility, /liability
│   └── Stage: prod
│
└── IAM
    ├── Role: BedrockAgentExecutionRole
    ├── Role: LambdaExecutionRole
    └── Role: APIGatewayInvocationRole
```

### Deployment Steps

1. **Prerequisites**
   ```bash
   # Create Knowledge Base (via CloudFormation or console)
   # Configure AWS credentials
   aws configure
   ```

2. **Deploy Lambda Functions**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Create Bedrock Agent**
   ```bash
   python create_agent.py
   # Saves: agent_config.json, kb_config.json
   ```

4. **Set Up Memory**
   ```bash
   python 03_create_memory.py
   # Saves: memory_config.json
   ```

5. **Configure Authentication**
   ```bash
   python 08_create_cognito.py
   # Saves: cognito_config.json
   ```

6. **Create API Gateway**
   ```bash
   python 11_create_gateway.py
   # Saves: gateway_config.json
   ```

7. **Integrate Lambda with Gateway**
   ```bash
   python 12_add_lambda_to_gateway.py
   # Saves: lambda_integration_config.json
   ```

8. **Test Deployment**
   ```bash
   python 02_test_agent.py
   python 15_test_full_agent.py
   ```

### Configuration Management

**Configuration Files** (generated during deployment):
- `agent_config.json` - Agent ID and details
- `kb_config.json` - Knowledge Base configuration
- `memory_config.json` - Memory ID
- `cognito_config.json` - Authentication details
- `gateway_config.json` - API Gateway URL
- `lambda_config.json` - Lambda ARNs
- `lambda_integration_config.json` - Integration details

**Environment Variables** (for MCP server):
```bash
export COGNITO_DOMAIN_PREFIX="your-domain"
export COGNITO_CLIENT_ID="your-client-id"
export COGNITO_CLIENT_SECRET="your-secret"
export API_GATEWAY_URL="https://api.execute-api.region.amazonaws.com/prod"
```

### Monitoring and Logging

**CloudWatch Logs**:
- `/aws/lambda/check_eligibility` - Eligibility function logs
- `/aws/lambda/calculate_liability` - Liability function logs
- `/aws/bedrock/agent/{agent-id}` - Agent invocation logs
- `/aws/apigateway/{api-id}` - API Gateway logs

**CloudWatch Metrics**:
- `Bedrock.InvokeAgent.Invocations` - Agent invocation count
- `Bedrock.InvokeAgent.Latency` - Response time
- `Lambda.Invocations` - Lambda execution count
- `Lambda.Errors` - Lambda error count
- `APIGateway.Count` - API request count
- `APIGateway.4XXError` - Client errors
- `APIGateway.5XXError` - Server errors

**CloudWatch Alarms**:
- High error rate (> 5%)
- High latency (> 2 seconds)
- Throttling events
- Failed authentications


## Testing Strategy

### 1. Unit Testing

**Lambda Functions**:
```python
# Test eligibility check logic
def test_check_eligibility_active_member():
    result = check_eligibility("M001", "2024-03-15")
    assert result['is_eligible'] == True
    assert result['enrollment_status'] == "ACTIVE"

def test_check_eligibility_inactive_member():
    result = check_eligibility("M002", "2024-03-15")
    assert result['is_eligible'] == False
    assert result['reason_code'] == "NOT_ENROLLED"

# Test liability calculation logic
def test_calculate_liability_with_copay():
    result = calculate_liability("M001", "99213", 200.00, "2024-03-15")
    assert result['total_liability'] > 0
    assert 'breakdown' in result
```

### 2. Integration Testing

**Agent Workflow Testing**:
```python
# Test complete workflow
def test_agent_workflow():
    # 1. Check eligibility
    response1 = invoke_agent("Check if member M001 is eligible")
    assert "eligible" in response1.lower()
    
    # 2. Calculate liability
    response2 = invoke_agent("Calculate liability for M001, service 99213, $200")
    assert "liability" in response2.lower()
    
    # 3. Search knowledge base
    response3 = invoke_agent("What are the copay amounts for office visits?")
    assert "copay" in response3.lower()
```

**Dry-Run Testing**:
- All scripts have `_dryrun.py` versions
- Simulate API calls without AWS credentials
- Validate logic and error handling
- Generate sample configuration files

### 3. End-to-End Testing

**Full System Test**:
```python
# Test complete flow: Client → API Gateway → Agent → Lambda
def test_e2e_eligibility_check():
    # 1. Get OAuth token
    token = get_oauth_token()
    
    # 2. Call API Gateway
    response = requests.post(
        f"{api_url}/eligibility",
        headers={"Authorization": f"Bearer {token}"},
        json={"member_id": "M001", "service_date": "2024-03-15"}
    )
    
    # 3. Verify response
    assert response.status_code == 200
    data = response.json()
    assert data['is_eligible'] == True
```

### 4. Memory Testing

**Memory Persistence Test**:
```python
# Test memory across sessions
def test_memory_persistence():
    # Session 1: Store preference
    response1 = invoke_agent("I prefer email communication", session_id="test-123")
    
    # Session 2: Recall preference
    response2 = invoke_agent("How should I contact you?", session_id="test-123")
    assert "email" in response2.lower()
```

### 5. Performance Testing

**Load Testing**:
```python
# Test concurrent requests
import concurrent.futures

def test_concurrent_requests():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(invoke_agent, f"Check eligibility for M{i:03d}")
            for i in range(100)
        ]
        results = [f.result() for f in futures]
    
    # Verify all succeeded
    assert all(r['statusCode'] == 200 for r in results)
```

**Latency Testing**:
```python
# Measure response times
def test_response_latency():
    start = time.time()
    response = invoke_agent("Check eligibility for M001")
    latency = time.time() - start
    
    # Should respond within 2 seconds
    assert latency < 2.0
```

### 6. Security Testing

**Authentication Testing**:
```python
# Test invalid token
def test_invalid_token():
    response = requests.post(
        f"{api_url}/eligibility",
        headers={"Authorization": "Bearer invalid-token"},
        json={"member_id": "M001"}
    )
    assert response.status_code == 401

# Test expired token
def test_expired_token():
    # Use token from 2 hours ago
    old_token = get_expired_token()
    response = requests.post(
        f"{api_url}/eligibility",
        headers={"Authorization": f"Bearer {old_token}"},
        json={"member_id": "M001"}
    )
    assert response.status_code == 401
```

### 7. Test Scripts

**Available Test Scripts**:
- `02_test_agent.py` - Agent workflow testing
- `02_test_agent_dryrun.py` - Dry-run agent testing
- `05_test_memory.py` - Memory retrieval testing
- `05_test_memory_dryrun.py` - Dry-run memory testing
- `15_test_full_agent.py` - Full agent functionality testing

**Test Execution**:
```bash
# Run dry-run tests (no AWS credentials needed)
python 02_test_agent_dryrun.py
python 05_test_memory_dryrun.py

# Run production tests
python 02_test_agent.py
python 05_test_memory.py
python 15_test_full_agent.py
```

## Performance Considerations

### 1. Latency Optimization

**Target Latencies**:
- Agent invocation: < 2 seconds
- Lambda execution: < 500ms
- Knowledge Base retrieval: < 1 second
- API Gateway overhead: < 100ms

**Optimization Strategies**:
- Lambda warm-up (provisioned concurrency)
- Knowledge Base index optimization
- Efficient Lambda code (minimal dependencies)
- Connection pooling for database access
- Caching frequently accessed data

### 2. Throughput

**Capacity**:
- API Gateway: 10,000 requests/second
- Lambda: 1,000 concurrent executions (default)
- Bedrock Agent: Based on model quotas
- Cognito: 120 requests/second (token endpoint)

**Scaling**:
- Lambda: Automatic scaling
- API Gateway: Automatic scaling
- Bedrock: Request quota increases via AWS Support
- Cognito: Quota increases via AWS Support

### 3. Cost Optimization

**Cost Factors**:
- Bedrock Agent invocations: Per-request pricing
- Lambda executions: Per-invocation + duration
- API Gateway: Per-request pricing
- Knowledge Base: Storage + retrieval
- Cognito: Free tier available

**Optimization Strategies**:
- Efficient prompts (reduce token usage)
- Lambda memory optimization
- Knowledge Base result limiting
- Caching responses where appropriate
- Reserved capacity for predictable workloads

### 4. Memory Management

**Agent Memory**:
- Session summary: 2,000 tokens max
- User preferences: 1,000 tokens max
- Semantic memory: 3,000 tokens max
- Retention: 30 days
- Automatic cleanup of expired sessions

**Lambda Memory**:
- Eligibility function: 256 MB
- Liability function: 512 MB
- Benefit lookup: 256 MB
- Adjust based on actual usage

### 5. Caching Strategy

**API Gateway Caching**:
```python
# Enable caching for GET requests
cache_config = {
    "cacheClusterEnabled": True,
    "cacheClusterSize": "0.5",  # GB
    "cacheTtlInSeconds": 300     # 5 minutes
}
```

**Lambda Response Caching**:
```python
# Cache eligibility results
@cache(ttl=300)  # 5 minutes
def check_eligibility(member_id, service_date):
    # Expensive operation
    return result
```

**Knowledge Base Caching**:
- Bedrock automatically caches KB results
- No explicit configuration needed

## Maintenance and Operations

### 1. Monitoring Dashboard

**Key Metrics**:
- Request count (per minute)
- Error rate (percentage)
- Average latency (milliseconds)
- Token usage (per request)
- Memory usage (MB)
- Cost (per day)

**CloudWatch Dashboard**:
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Bedrock", "InvokeAgent.Invocations"],
          ["AWS/Lambda", "Invocations"],
          ["AWS/ApiGateway", "Count"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "Request Volume"
      }
    }
  ]
}
```

### 2. Alerting

**Critical Alerts**:
- Error rate > 5%
- Latency > 2 seconds (p95)
- Lambda throttling
- API Gateway 5XX errors
- Cognito authentication failures

**Alert Configuration**:
```python
alarm = cloudwatch.Alarm(
    alarm_name="HighErrorRate",
    comparison_operator="GreaterThanThreshold",
    evaluation_periods=2,
    metric_name="Errors",
    namespace="AWS/Lambda",
    period=300,
    statistic="Sum",
    threshold=10,
    actions_enabled=True,
    alarm_actions=[sns_topic_arn]
)
```

### 3. Backup and Recovery

**Configuration Backup**:
- Store all `*_config.json` files securely
- Version control for scripts
- Document manual configuration steps

**Disaster Recovery**:
- Agent can be recreated from scripts
- Lambda functions redeployable
- API Gateway configuration exportable
- Cognito user pool backup

### 4. Updates and Versioning

**Agent Updates**:
```python
# Create new agent version
response = bedrock_agent.create_agent_version(
    agentId=agent_id,
    description="Updated system prompt"
)

# Create new alias pointing to version
response = bedrock_agent.create_agent_alias(
    agentId=agent_id,
    agentAliasName="PROD-v2",
    agentVersion=version_number
)
```

**Lambda Updates**:
```bash
# Update function code
aws lambda update-function-code \
    --function-name check_eligibility \
    --zip-file fileb://function.zip

# Publish new version
aws lambda publish-version \
    --function-name check_eligibility
```

### 5. Troubleshooting

**Common Issues**:

1. **Agent not responding**
   - Check CloudWatch logs
   - Verify IAM permissions
   - Check Lambda function status

2. **Authentication failures**
   - Verify Cognito configuration
   - Check token expiration
   - Validate client credentials

3. **High latency**
   - Check Lambda cold starts
   - Review Knowledge Base query complexity
   - Optimize Lambda code

4. **Memory errors**
   - Increase Lambda memory
   - Review memory retention settings
   - Check for memory leaks

**Debug Mode**:
```python
# Enable detailed tracing
response = bedrock_agent_runtime.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId=session_id,
    inputText=query,
    enableTrace=True  # Enable detailed trace
)

# Review trace
print(json.dumps(response['trace'], indent=2))
```

## Future Enhancements

### Planned Features

1. **Multi-Language Support**
   - Support for Spanish, French, etc.
   - Language detection
   - Translated responses

2. **Advanced Analytics**
   - Usage patterns analysis
   - Cost optimization recommendations
   - Performance insights

3. **Enhanced Memory**
   - Long-term memory (> 30 days)
   - Cross-session learning
   - Personalization engine

4. **Additional Tools**
   - Provider network lookup
   - Prior authorization check
   - Claims status tracking
   - Benefit comparison

5. **Integration Expansion**
   - EHR system integration
   - Claims processing system
   - Member portal integration
   - Mobile app SDK

### Roadmap

**Q2 2024**:
- Multi-language support
- Enhanced analytics dashboard
- Additional Lambda tools

**Q3 2024**:
- Long-term memory implementation
- EHR integration
- Mobile SDK

**Q4 2024**:
- Advanced personalization
- Predictive analytics
- Self-service portal

## Conclusion

The AWS Bedrock Member Liability Agent provides a comprehensive, scalable solution for automating member benefits eligibility verification and liability calculations. The design leverages AWS managed services for reliability, security, and performance while maintaining flexibility for future enhancements.

### Key Strengths

- **Intelligent Automation**: Claude 3 Sonnet provides natural language understanding
- **Extensible Architecture**: Easy to add new tools and capabilities
- **Secure by Design**: OAuth 2.0, IAM roles, encryption at rest and in transit
- **Scalable**: Automatic scaling with AWS managed services
- **Observable**: Comprehensive logging and monitoring
- **Cost-Effective**: Pay-per-use pricing model

### Success Metrics

- Response time < 2 seconds (95th percentile)
- Error rate < 1%
- User satisfaction > 90%
- Cost per request < $0.10
- Availability > 99.9%

---

**Document Version**: 1.0.0  
**Last Updated**: March 15, 2024  
**Next Review**: June 15, 2024
