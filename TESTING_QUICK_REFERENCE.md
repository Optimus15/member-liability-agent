# Testing Quick Reference

## Test Scripts Comparison

### test_agent.py (General Testing)
```bash
# Run all tests
python3 test_agent.py

# Run specific test type
python3 test_agent.py eligibility
python3 test_agent.py liability
python3 test_agent.py kb
python3 test_agent.py combined

# Interactive mode
python3 test_agent.py interactive
```

**Use when**: You want to test individual features or explore the agent interactively.

### 02_test_agent.py (Workflow Testing)
```bash
# Default workflow test
python3 02_test_agent.py

# Custom member and date
python3 02_test_agent.py M789012 2024-06-20

# Full custom parameters
python3 02_test_agent.py M123456 2024-03-15 250.00
```

**Use when**: You want to test the complete workflow from eligibility to liability calculation.

## Quick Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Deploy Lambda functions
./deploy.sh

# Create agent
python3 create_agent.py
```

### Testing
```bash
# Quick workflow test
python3 02_test_agent.py

# Test with trace enabled (already enabled in 02_test_agent.py)
# View detailed execution flow

# Check results
cat test_results_*.json | jq .
```

### Debugging
```bash
# View agent logs
aws logs tail /aws/bedrock/agents/<AGENT_ID> --follow

# View Lambda logs
aws logs tail /aws/lambda/member-liability-check-eligibility --follow
aws logs tail /aws/lambda/member-liability-calculate --follow

# Test Lambda directly
aws lambda invoke \
  --function-name member-liability-check-eligibility \
  --payload '{"parameters":[{"name":"memberId","value":"M123"}]}' \
  response.json
```

## Test Workflow

```
02_test_agent.py Workflow:

1. Check Eligibility
   ├─ Query: "Is member eligible?"
   ├─ Invokes: check_eligibility Lambda
   └─ Result: ✅ ELIGIBLE or ❌ INELIGIBLE

2. Check Benefits (if eligible)
   ├─ Query: "Does member have benefits?"
   ├─ Uses: Knowledge Base (if available)
   └─ Result: ✅ HAS BENEFITS or ⚠️ UNCLEAR

3. Calculate Liability (if eligible)
   ├─ Query: "Calculate liability for $X claim"
   ├─ Invokes: calculate_member_liability Lambda
   └─ Result: ✅ COMPLETED or ❌ FAILED

4. Search Knowledge Base
   ├─ Query: "Search for policy rules"
   ├─ Uses: Knowledge Base retrieve tool
   └─ Result: ✅ COMPLETED or ⚠️ SKIPPED
```

## Expected Outputs

### Successful Test
```
✅ Eligibility Check: PASSED
✅ Benefits Check: PASSED
✅ Liability Calculation: COMPLETED
✅ Knowledge Base Search: COMPLETED

📄 Test results saved to: test_results_workflow-test-1710501000.json
```

### Partial Success
```
✅ Eligibility Check: PASSED
⚠️  Benefits Check: UNCLEAR
✅ Liability Calculation: COMPLETED
⚠️  Knowledge Base Search: SKIPPED/FAILED
```

### Failure
```
❌ Eligibility Check: FAILED

⚠️  WORKFLOW STOPPED: Member is not eligible
```

## Common Issues

| Issue | Solution |
|-------|----------|
| agent_config.json not found | Run `create_agent.py` |
| Lambda timeout | Increase timeout in Lambda config |
| KB ID is placeholder | Update kb_config.json with real KB ID |
| Agent not responding | Check CloudWatch logs |
| Permission denied | Verify IAM roles and policies |

## Result Files

Test results are saved to JSON files:
```
test_results_workflow-test-{timestamp}.json
```

View results:
```bash
# Pretty print
cat test_results_*.json | jq .

# Extract specific field
cat test_results_*.json | jq '.results.eligibility.is_eligible'

# View all test timestamps
cat test_results_*.json | jq '.test_timestamp'
```

## Test Data

### Default Test Data
- Member ID: M123456
- Service Date: 2024-03-15
- Claim Amount: $150.00

### Mock Data in Lambda Functions
The Lambda functions use mock data. Update with real data:
- Member database queries
- Claims database queries
- Policy rules retrieval

## Validation Checklist

Before running tests:
- [ ] Agent created and prepared
- [ ] Lambda functions deployed
- [ ] Lambda ARNs updated in agent config
- [ ] Knowledge Base created (optional)
- [ ] AWS credentials configured
- [ ] agent_config.json exists

After running tests:
- [ ] All steps completed
- [ ] Results saved to JSON
- [ ] No errors in CloudWatch logs
- [ ] Response times acceptable (< 2s)
- [ ] Calculations are accurate

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Eligibility Check | < 500ms | ___ |
| Benefits Check | < 1000ms | ___ |
| Liability Calculation | < 1000ms | ___ |
| KB Search | < 2000ms | ___ |
| Total Workflow | < 5000ms | ___ |

## Next Steps After Testing

1. ✅ Verify all tests pass
2. ✅ Review result files
3. ✅ Check CloudWatch logs
4. ✅ Validate calculations
5. ✅ Test edge cases
6. ✅ Load testing
7. ✅ Deploy to production

## Support Resources

- **Setup Guide**: SETUP_GUIDE.md
- **Test Documentation**: 02_TEST_DOCUMENTATION.md
- **Architecture**: ARCHITECTURE.md
- **Full README**: README.md
- **AWS Docs**: https://docs.aws.amazon.com/bedrock/

---

**Quick Test**: `python3 02_test_agent.py`
