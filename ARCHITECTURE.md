# Benefits Member Liability Agent - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           User/Application                           │
│                    (Healthcare Provider, Member Portal)              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Query: "Check eligibility for M123456"
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AWS Bedrock Agent                               │
│                   (Claude 3 Sonnet Model)                            │
│                                                                       │
│  System Prompt:                                                      │
│  "You are the Benefits and Member Liability Agent..."                │
│                                                                       │
│  Capabilities:                                                       │
│  1. Natural language understanding                                   │
│  2. Tool orchestration                                               │
│  3. Response generation                                              │
└───────────┬─────────────────┬─────────────────┬──────────────────────┘
            │                 │                 │
            │                 │                 │
            ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Knowledge Base  │ │  Action Group 1  │ │  Action Group 2  │
│   (Retrieve)     │ │ check_eligibility│ │calculate_liability│
└──────────────────┘ └──────────────────┘ └──────────────────┘
         │                    │                     │
         │                    │                     │
         ▼                    ▼                     ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   S3 Bucket      │ │  Lambda Function │ │  Lambda Function │
│ Policy Documents │ │  Eligibility     │ │  Liability       │
│ Plan Details     │ │  Check           │ │  Calculation     │
│ Coverage Rules   │ └──────────────────┘ └──────────────────┘
└──────────────────┘          │                     │
                              │                     │
                              ▼                     ▼
                    ┌─────────────────────────────────────┐
                    │         Data Layer                   │
                    │  ┌──────────┐  ┌──────────┐        │
                    │  │ Members  │  │  Claims  │        │
                    │  │   DB     │  │    DB    │        │
                    │  └──────────┘  └──────────┘        │
                    └─────────────────────────────────────┘
```

## Component Details

### 1. Bedrock Agent (Orchestrator)

**Model**: Claude 3 Sonnet (anthropic.claude-3-sonnet-20240229-v1:0)

**Responsibilities**:
- Parse user queries
- Determine which tools to invoke
- Orchestrate multi-step workflows
- Generate natural language responses
- Maintain conversation context

**Configuration**:
- Foundation Model: Claude 3 Sonnet
- Idle Session TTL: 30 minutes
- Agent Role: BenefitsMemberLiabilityAgentRole

### 2. Knowledge Base (Retrieval)

**Purpose**: Provide context about policies, plans, and coverage

**Data Sources**:
- Policy rule documents
- Plan benefit details
- Coverage guidelines
- Service code mappings
- Authorization requirements

**Retrieval Process**:
1. Agent identifies need for policy information
2. Generates search query
3. Knowledge Base retrieves relevant documents
4. Agent uses context to formulate response

**Configuration**:
- State: ENABLED
- Description: "Benefits policy rules, plan details, and coverage information"

### 3. Action Group: check_eligibility

**Lambda Function**: `member-liability-check-eligibility`

**API Endpoint**: POST /check-eligibility

**Input Schema**:
```json
{
  "memberId": "string (required)",
  "serviceDate": "string (required, YYYY-MM-DD)",
  "benefitCode": "string (optional)"
}
```

**Output Schema**:
```json
{
  "isEligible": "boolean",
  "enrollmentStatus": "string",
  "coveragePeriod": {
    "startDate": "string",
    "endDate": "string"
  },
  "applicablePolicyRules": "array",
  "ineligibilityReason": "string (if not eligible)",
  "reasonCode": "string (if not eligible)"
}
```

**Processing Flow**:
1. Receive member ID and service date
2. Query member database for enrollment status
3. Verify service date within coverage period
4. Retrieve applicable policy rules
5. Return eligibility result

### 4. Action Group: calculate_member_liability

**Lambda Function**: `member-liability-calculate`

**API Endpoint**: POST /calculate-liability

**Input Schema**:
```json
{
  "memberId": "string (required)",
  "claimId": "string (required)",
  "serviceCode": "string (optional)",
  "totalCharges": "number (optional)"
}
```

**Output Schema**:
```json
{
  "totalLiability": "number",
  "breakdown": {
    "deductibleAmount": "number",
    "copayAmount": "number",
    "coinsuranceAmount": "number",
    "outOfPocketApplied": "number",
    "remainingDeductible": "number",
    "remainingOutOfPocket": "number"
  },
  "calculationSteps": "array",
  "appliedRules": "array"
}
```

**Processing Flow**:
1. Receive member ID and claim ID
2. Retrieve member plan details
3. Get claim information
4. Fetch applicable policy rules
5. Calculate deductible amount
6. Apply copay (if applicable)
7. Calculate coinsurance
8. Apply out-of-pocket maximum
9. Generate calculation audit trail
10. Return liability breakdown

## Data Flow Examples

### Example 1: Eligibility Check

```
User: "Check eligibility for member M123456 on 2024-03-15"
  │
  ▼
Agent: Parses query, identifies need for eligibility check
  │
  ▼
Agent: Invokes check_eligibility action group
  │
  ▼
Lambda: Queries member database
  │
  ├─ Member found: M123456
  ├─ Enrollment status: ACTIVE
  ├─ Coverage period: 2024-01-01 to 2024-12-31
  └─ Service date 2024-03-15 is within period ✓
  │
  ▼
Lambda: Retrieves policy rules for member's plan
  │
  ├─ Rule 1: Apply $1000 deductible
  ├─ Rule 2: $25 copay for primary care
  └─ Rule 3: 20% coinsurance after deductible
  │
  ▼
Lambda: Returns eligibility result
  │
  ▼
Agent: Generates natural language response
  │
  ▼
User: "Member M123456 is eligible for benefits. They have an active 
       enrollment with coverage from January 1 to December 31, 2024. 
       The applicable policy rules include a $1000 annual deductible, 
       $25 copay for primary care visits, and 20% coinsurance after 
       the deductible is met."
```

### Example 2: Liability Calculation

```
User: "Calculate liability for member M123456 for a $150 office visit"
  │
  ▼
Agent: Parses query, identifies need for liability calculation
  │
  ▼
Agent: Invokes calculate_member_liability action group
  │
  ▼
Lambda: Retrieves member data
  │
  ├─ Plan: PPO-001
  ├─ Deductible: $1000 (paid: $500, remaining: $500)
  └─ Out-of-pocket max: $5000 (paid: $1500, remaining: $3500)
  │
  ▼
Lambda: Applies policy rules
  │
  ├─ Step 1: Apply $25 copay
  ├─ Step 2: Remaining charges: $125
  ├─ Step 3: Apply to deductible: $125
  ├─ Step 4: Deductible not fully met, no coinsurance
  └─ Step 5: Total liability: $150 ($25 copay + $125 deductible)
  │
  ▼
Lambda: Returns calculation result with audit trail
  │
  ▼
Agent: Generates natural language response with breakdown
  │
  ▼
User: "For a $150 office visit, member M123456 will pay:
       - Copay: $25
       - Deductible: $125
       - Total: $150
       
       After this visit:
       - Remaining deductible: $375
       - Remaining out-of-pocket: $3350"
```

### Example 3: Combined Workflow

```
User: "I need to know if member M123456 is eligible and how much 
       they'll pay for a primary care visit on March 15"
  │
  ▼
Agent: Identifies need for both eligibility check AND liability calculation
  │
  ├─ Step 1: Check eligibility
  │   │
  │   ▼
  │   Invokes check_eligibility
  │   │
  │   ▼
  │   Result: Eligible ✓
  │
  ├─ Step 2: Calculate liability
  │   │
  │   ▼
  │   Invokes calculate_member_liability
  │   │
  │   ▼
  │   Result: $150 total liability
  │
  ▼
Agent: Combines results into comprehensive response
  │
  ▼
User: "Member M123456 is eligible for benefits on March 15, 2024. 
       For a primary care visit, they will pay $150 total, which 
       includes a $25 copay and $125 applied to their deductible."
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
└─────────────────────────────────────────────────────────────┘

1. Authentication & Authorization
   ├─ IAM Roles and Policies
   ├─ Bedrock Agent Role (assume role)
   ├─ Lambda Execution Role
   └─ Resource-based policies

2. Data Encryption
   ├─ In Transit: TLS 1.2+
   ├─ At Rest: AWS KMS
   └─ Knowledge Base: Encrypted storage

3. Network Security
   ├─ VPC Configuration (optional)
   ├─ Security Groups
   └─ Private endpoints

4. Audit & Compliance
   ├─ CloudTrail logging
   ├─ CloudWatch Logs
   ├─ Calculation audit trails
   └─ 7-year retention policy

5. Input Validation
   ├─ Lambda function validation
   ├─ OpenAPI schema validation
   └─ Bedrock Agent input filtering
```

## Scalability & Performance

### Horizontal Scaling
- **Bedrock Agent**: Automatically scales with request volume
- **Lambda Functions**: Auto-scales up to account limits
- **Knowledge Base**: Scales with query volume

### Performance Targets
- **Eligibility Check**: < 500ms
- **Liability Calculation**: < 1000ms
- **Knowledge Base Retrieval**: < 2000ms
- **Total Response Time**: < 2 seconds (per Requirement 9.1)

### Optimization Strategies
1. **Lambda**: 
   - Warm start optimization
   - Connection pooling for databases
   - Caching frequently accessed data

2. **Knowledge Base**:
   - Optimized document chunking
   - Efficient embedding generation
   - Query result caching

3. **Agent**:
   - Session management
   - Context window optimization
   - Streaming responses

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
└─────────────────────────────────────────────────────────────┘

CloudWatch Metrics
├─ Agent invocation count
├─ Lambda execution duration
├─ Error rates
├─ Knowledge Base retrieval latency
└─ Cost per request

CloudWatch Logs
├─ /aws/bedrock/agents/<AGENT_ID>
├─ /aws/lambda/member-liability-check-eligibility
└─ /aws/lambda/member-liability-calculate

CloudWatch Alarms
├─ High error rate (> 5%)
├─ Slow response time (> 3s)
├─ Lambda throttling
└─ Cost threshold exceeded

X-Ray Tracing (optional)
├─ End-to-end request tracing
├─ Service map visualization
└─ Performance bottleneck identification
```

## Deployment Architecture

```
Development → Staging → Production

Each environment has:
├─ Separate Bedrock Agent
├─ Separate Lambda functions
├─ Separate Knowledge Base
├─ Separate IAM roles
└─ Environment-specific configuration

CI/CD Pipeline:
1. Code commit
2. Automated tests
3. Lambda package build
4. Deploy to staging
5. Integration tests
6. Manual approval
7. Deploy to production
8. Smoke tests
```

## Cost Optimization

### Cost Breakdown
```
Component                 Cost Driver              Optimization
─────────────────────────────────────────────────────────────────
Bedrock Agent            Requests                 Batch queries
Claude 3 Sonnet          Tokens (input/output)    Concise prompts
Lambda Functions         Invocations + Duration   Optimize code
Knowledge Base           Storage + Retrieval      Efficient docs
CloudWatch               Logs + Metrics           Log filtering
```

### Cost Reduction Strategies
1. Use streaming responses to reduce token usage
2. Implement caching for frequently accessed data
3. Optimize Lambda memory allocation
4. Use log filtering to reduce storage costs
5. Implement request throttling to prevent abuse

---

This architecture provides a scalable, secure, and cost-effective solution for healthcare benefits eligibility verification and member liability calculations using AWS Bedrock.
