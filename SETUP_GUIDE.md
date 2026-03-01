# Benefits Member Liability Agent - Quick Setup Guide

## What You Have

A complete AWS Bedrock Agent implementation with:

1. **Main Agent Script** (`create_agent.py`)
   - Retrieves Knowledge Base ID from CloudFormation or uses placeholder
   - Creates Bedrock Agent with Claude 3 Sonnet
   - Configures 3 capabilities:
     - Knowledge Base retrieval (for policy rules and plan details)
     - check_eligibility tool (Lambda function)
     - calculate_member_liability tool (Lambda function)

2. **Lambda Functions**
   - `lambda_check_eligibility.py` - Checks member eligibility
   - `lambda_calculate_liability.py` - Calculates liability amounts

3. **Deployment Tools**
   - `deploy.sh` - Automated deployment script
   - `requirements.txt` - Python dependencies
   - `test_agent.py` - Test suite for the agent

4. **Documentation**
   - `README.md` - Comprehensive documentation
   - `SETUP_GUIDE.md` - This quick start guide

## Quick Start (5 Steps)

### Step 1: Install Dependencies

```bash
cd 01_member_liability_agent
pip install -r requirements.txt
```

### Step 2: Configure AWS

```bash
# Set your AWS region
export AWS_REGION=us-east-1

# Verify AWS credentials
aws sts get-caller-identity
```

### Step 3: Deploy Lambda Functions

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

This will:
- Create IAM role for Lambda functions
- Package and deploy both Lambda functions
- Display Lambda ARNs for next step

### Step 4: Update Lambda ARNs

Edit `create_agent.py` and replace placeholders:

```python
# Line ~150 and ~220
'lambda': 'arn:aws:lambda:REGION:ACCOUNT_ID:function:member-liability-check-eligibility'
# Replace with actual ARN from deploy.sh output
```

### Step 5: Create Bedrock Agent

```bash
python3 create_agent.py
```

This will:
1. Retrieve Knowledge Base ID (or use placeholder)
2. Create IAM role for agent
3. Create Bedrock Agent
4. Add custom tools (action groups)
5. Associate Knowledge Base
6. Create agent alias
7. Save configuration to `agent_config.json`

## Testing

### Quick Test

```bash
# Run all tests
python3 test_agent.py

# Run specific test
python3 test_agent.py eligibility
python3 test_agent.py liability
python3 test_agent.py kb

# Interactive mode
python3 test_agent.py interactive
```

### Manual Test (AWS Console)

1. Go to AWS Bedrock Console
2. Navigate to Agents
3. Select "benefits-member-liability-agent"
4. Click "Test" button
5. Try: "Check eligibility for member M123456 on 2024-03-15"

## Important Notes

### Knowledge Base Setup

If you don't have a Knowledge Base yet:

1. **Option A: Use CloudFormation**
   - Deploy a stack named 'knowledgebase'
   - Ensure it has output 'KnowledgeBaseId'
   - Script will auto-retrieve the ID

2. **Option B: Manual Setup**
   - Create KB in AWS Bedrock Console
   - Copy the KB ID
   - Update `kb_config.json` manually
   - Re-run `create_agent.py`

### Lambda Function Implementation

The provided Lambda functions are **templates** with mock data. You need to:

1. **Connect to your databases**
   ```python
   # Replace mock data with real queries
   dynamodb = boto3.resource('dynamodb')
   members_table = dynamodb.Table('members')
   member = members_table.get_item(Key={'memberId': member_id})
   ```

2. **Implement business logic**
   - Real eligibility verification
   - Accurate liability calculations
   - Policy rule evaluation

3. **Add error handling**
   - Input validation
   - Database error handling
   - Logging and monitoring

### Security Considerations

Before production deployment:

1. **IAM Permissions**: Review and restrict IAM roles
2. **Data Encryption**: Enable encryption at rest and in transit
3. **VPC Configuration**: Deploy Lambda in VPC if needed
4. **Secrets Management**: Use AWS Secrets Manager for credentials
5. **Audit Logging**: Enable CloudTrail and CloudWatch Logs

## Troubleshooting

### Agent Creation Fails

**Error**: "Bedrock service not available"
- **Solution**: Enable Bedrock in your AWS region
- Check: AWS Console → Bedrock → Get Started

**Error**: "IAM role creation failed"
- **Solution**: Ensure you have IAM permissions
- Required: `iam:CreateRole`, `iam:PutRolePolicy`

**Error**: "Knowledge Base not found"
- **Solution**: Create KB first or use placeholder
- Update `kb_config.json` with actual KB ID later

### Lambda Deployment Fails

**Error**: "Role not found"
- **Solution**: Wait 10-15 seconds for IAM propagation
- Re-run `deploy.sh`

**Error**: "Function already exists"
- **Solution**: Script will update existing function
- Or delete manually: `aws lambda delete-function --function-name <name>`

### Agent Not Responding

1. **Check CloudWatch Logs**
   ```bash
   aws logs tail /aws/bedrock/agents/<AGENT_ID> --follow
   ```

2. **Verify Lambda ARNs**
   - Go to Bedrock Console
   - Check action group configurations
   - Ensure Lambda ARNs are correct

3. **Test Lambda Directly**
   ```bash
   aws lambda invoke \
     --function-name member-liability-check-eligibility \
     --payload '{"parameters":[{"name":"memberId","value":"M123"}]}' \
     response.json
   ```

## Next Steps

1. **Customize Lambda Functions**
   - Connect to your databases
   - Implement real business logic
   - Add comprehensive error handling

2. **Populate Knowledge Base**
   - Upload policy documents
   - Add plan details
   - Include coverage information

3. **Test Thoroughly**
   - Run test suite
   - Test edge cases
   - Validate calculations

4. **Deploy to Production**
   - Set up CI/CD pipeline
   - Configure monitoring and alerts
   - Implement backup and disaster recovery

5. **Integrate with Systems**
   - Connect to claims processing system
   - Integrate with member portal
   - Add to provider applications

## Cost Estimate

For 1000 requests/day:

- **Bedrock Agent**: ~$0.50/day
- **Claude 3 Sonnet**: ~$2-5/day (depends on response length)
- **Lambda**: ~$0.10/day
- **Knowledge Base**: ~$0.20/day
- **Total**: ~$3-6/day or $90-180/month

## Support Resources

- **AWS Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **Bedrock Agents Guide**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- **Lambda Documentation**: https://docs.aws.amazon.com/lambda/
- **CloudWatch Logs**: https://docs.aws.amazon.com/cloudwatch/

## Files Reference

```
01_member_liability_agent/
├── create_agent.py              # Main agent creation script
├── lambda_check_eligibility.py  # Eligibility check Lambda
├── lambda_calculate_liability.py # Liability calculation Lambda
├── deploy.sh                    # Deployment automation
├── test_agent.py               # Test suite
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation
├── SETUP_GUIDE.md             # This quick start guide
├── kb_config_template.json    # KB config template
├── kb_config.json             # Generated KB config
└── agent_config.json          # Generated agent config
```

## Quick Commands Reference

```bash
# Deploy everything
./deploy.sh && python3 create_agent.py

# Test agent
python3 test_agent.py

# View logs
aws logs tail /aws/bedrock/agents/<AGENT_ID> --follow

# Update Lambda code
aws lambda update-function-code \
  --function-name member-liability-check-eligibility \
  --zip-file fileb://check_eligibility.zip

# Delete agent (cleanup)
aws bedrock-agent delete-agent --agent-id <AGENT_ID>
```

---

**Ready to deploy?** Start with Step 1 above! 🚀
