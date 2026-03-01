# 02_test_agent.py - Workflow Test Documentation

## Overview

This test script validates the Benefits Member Liability Agent through a specific workflow that mirrors real-world usage:

1. **Check Member Eligibility** - Verify if member is eligible for benefits
2. **Verify Benefits** - Confirm member has benefits available
3. **Calculate Liability** - Compute member liability once eligibility is validated
4. **Search Knowledge Base** - Retrieve policy information from knowledge base

## Usage

### Basic Usage

```bash
python3 02_test_agent.py
```

Uses default values:
- Member ID: M123456
- Service Date: 2024-03-15
- Claim Amount: $150.00

### Custom Parameters

```bash
python3 02_test_agent.py [member_id] [service_date] [claim_amount]
```

**Examples:**

```bash
# Test with specific member
python3 02_test_agent.py M789012 2024-06-20

# Test with custom claim amount
python3 02_test_agent.py M123456 2024-03-15 250.00

# Full custom test
python3 02_test_agent.py M345678 2024-12-01 500.00
```

## Workflow Steps

### Step 1: Check Member Eligibility

**Query**: "Is member {member_id} eligible for benefits on {service_date}?"

**What it tests**:
- Member enrollment status retrieval
- Coverage period validation
- Eligibility determination logic
- Action group: `check_eligibility`

**Success criteria**:
- Response indicates member is eligible
- No "not eligible" or "ineligible" in response

**Output**:
```
STEP 1: Checking Member Eligibility
================================================================================
🤖 Query: Is member M123456 eligible for benefits on 2024-03-15?
================================================================================

[Agent Response]

✅ Result: Member appears to be ELIGIBLE
```

### Step 2: Check Member Benefits

**Query**: "Does member {member_id} have benefits? What benefits are available?"

**What it tests**:
- Benefits information retrieval
- Plan details access
- Coverage information
- Knowledge Base integration (if available)

**Success criteria**:
- Response mentions benefits
- Benefit details are provided

**Output**:
```
STEP 2: Checking Member Benefits
================================================================================
🤖 Query: Does member M123456 have benefits? What benefits are available?
================================================================================

[Agent Response]

✅ Result: Member appears to HAVE benefits
```

### Step 3: Calculate Member Liability

**Query**: "Calculate the member liability for member {member_id} for a ${amount} claim..."

**What it tests**:
- Liability calculation logic
- Deductible application
- Copay calculation
- Coinsurance calculation
- Out-of-pocket maximum enforcement
- Action group: `calculate_member_liability`

**Success criteria**:
- Calculation completes without error
- Breakdown includes all components

**Output**:
```
STEP 3: Calculating Member Liability
================================================================================
🤖 Query: Calculate the member liability for member M123456 for a $150.00 claim...
================================================================================

[Agent Response with breakdown]

✅ Result: Liability calculation completed
```

### Step 4: Search Knowledge Base

**Query**: "Search the knowledge base for information about policy rules..."

**What it tests**:
- Knowledge Base integration
- Retrieve tool functionality
- Policy document access
- Context retrieval

**Success criteria**:
- Knowledge Base returns relevant information
- Policy rules are retrieved

**Output**:
```
STEP 4: Searching Knowledge Base
================================================================================
🤖 Query: Search the knowledge base for information about policy rules...
================================================================================

[Agent Response with KB information]

✅ Result: Knowledge base search completed
```

**Note**: If Knowledge Base ID is placeholder, this step is skipped with a warning.

## Features

### Session Continuity

The script uses a single session ID for all steps, allowing the agent to:
- Maintain conversation context
- Reference previous responses
- Build on earlier information

### Trace Information

Enable trace output to see:
- Which action groups are invoked
- Tool execution details
- Knowledge Base retrieval operations
- Agent reasoning steps

### Result Persistence

Test results are automatically saved to:
```
test_results_{session_id}.json
```

**Result file structure**:
```json
{
  "test_timestamp": "2024-03-15 10:30:00",
  "session_id": "workflow-test-1710501000",
  "parameters": {
    "member_id": "M123456",
    "service_date": "2024-03-15",
    "claim_amount": 150.0
  },
  "results": {
    "eligibility": {
      "is_eligible": true,
      "response": "...",
      "success": true
    },
    "benefits": {
      "has_benefits": true,
      "response": "...",
      "success": true
    },
    "liability": {
      "response": "...",
      "success": true
    },
    "knowledge_base": {
      "response": "...",
      "success": true
    }
  }
}
```

### Workflow Control

The script implements intelligent workflow control:

1. **If member is NOT eligible**:
   - Workflow stops after Step 1
   - Steps 2-4 are skipped
   - Clear message displayed

2. **If benefits are unclear**:
   - Warning displayed
   - Workflow continues to liability calculation
   - Allows testing even with incomplete data

3. **If Knowledge Base is not configured**:
   - Step 4 is skipped
   - Warning message displayed
   - Other steps continue normally

## Output Examples

### Successful Workflow

```
================================================================================
Benefits Member Liability Agent - Workflow Test
================================================================================
Agent ID: AGENT123456
Alias ID: ALIAS123456
Knowledge Base ID: KB789012

Test Parameters:
  Member ID: M123456
  Service Date: 2024-03-15
  Claim Amount: $150.00
================================================================================

[Steps 1-4 execute...]

================================================================================
WORKFLOW SUMMARY
================================================================================
✅ Eligibility Check: PASSED
✅ Benefits Check: PASSED
✅ Liability Calculation: COMPLETED
✅ Knowledge Base Search: COMPLETED
================================================================================

📄 Test results saved to: test_results_workflow-test-1710501000.json

✅ Workflow test completed successfully!
```

### Failed Eligibility

```
STEP 1: Checking Member Eligibility
================================================================================
[Response indicating ineligibility]

❌ Result: Member appears to be INELIGIBLE or status unclear

================================================================================
⚠️  WORKFLOW STOPPED: Member is not eligible
================================================================================

Cannot proceed with benefits check and liability calculation.
```

## Troubleshooting

### Error: agent_config.json not found

**Solution**: Run `create_agent.py` first to create the agent and generate configuration.

```bash
python3 create_agent.py
```

### Error: Failed to invoke agent

**Possible causes**:
1. Agent not created or not prepared
2. AWS credentials not configured
3. Incorrect agent ID or alias ID
4. Region mismatch

**Solutions**:
- Verify agent exists in AWS Bedrock Console
- Check AWS credentials: `aws sts get-caller-identity`
- Verify agent_config.json has correct IDs
- Ensure AWS_REGION environment variable is set

### Warning: Knowledge Base ID is placeholder

**Solution**: Update kb_config.json with actual Knowledge Base ID:

```json
{
  "knowledge_base_id": "YOUR_ACTUAL_KB_ID",
  "created_at": "2024-03-15T10:30:00",
  "source": "manual"
}
```

Then re-run `create_agent.py` to associate the Knowledge Base.

### Lambda Function Errors

If action groups fail:
1. Check Lambda functions are deployed
2. Verify Lambda ARNs in agent configuration
3. Check Lambda execution role permissions
4. Review CloudWatch logs for Lambda errors

## Comparison with test_agent.py

| Feature | test_agent.py | 02_test_agent.py |
|---------|---------------|------------------|
| Purpose | General testing | Specific workflow |
| Test Types | Multiple independent tests | Sequential workflow |
| Session | Multiple sessions | Single session |
| Workflow | Separate test functions | Integrated workflow |
| Validation | Manual observation | Automated checks |
| Results | Console only | Saved to JSON file |
| Trace | Optional | Enabled by default |
| Control Flow | Independent tests | Conditional execution |

## Best Practices

1. **Run after deployment**: Test immediately after deploying agent and Lambda functions

2. **Test with real data**: Use actual member IDs and dates when possible

3. **Review trace output**: Check which tools are being invoked

4. **Examine result files**: Review saved JSON for detailed analysis

5. **Test edge cases**: Try with:
   - Ineligible members
   - Expired coverage periods
   - High claim amounts
   - Different service dates

6. **Monitor CloudWatch**: Check logs during test execution

7. **Iterate on failures**: If tests fail, check:
   - Lambda function implementation
   - Agent configuration
   - Knowledge Base content
   - IAM permissions

## Integration with CI/CD

This test can be integrated into CI/CD pipelines:

```bash
# In your CI/CD script
python3 02_test_agent.py M123456 2024-03-15 150.00

# Check exit code
if [ $? -eq 0 ]; then
    echo "Agent workflow test passed"
else
    echo "Agent workflow test failed"
    exit 1
fi
```

## Next Steps

After successful testing:

1. **Deploy to production**: Promote agent to production environment
2. **Add more test cases**: Create additional workflow tests
3. **Implement monitoring**: Set up CloudWatch alarms
4. **Document results**: Share test results with stakeholders
5. **Integrate with systems**: Connect to production databases
6. **Load testing**: Test with multiple concurrent requests
7. **Security review**: Validate IAM permissions and data encryption

## Support

For issues or questions:
- Check CloudWatch logs: `/aws/bedrock/agents/<AGENT_ID>`
- Review Lambda logs: `/aws/lambda/member-liability-*`
- Examine saved result files
- Refer to SETUP_GUIDE.md for troubleshooting
