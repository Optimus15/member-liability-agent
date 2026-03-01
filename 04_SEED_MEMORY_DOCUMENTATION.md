# Memory Seeding Script Documentation

## Overview

The `04_seed_memory.py` script adds sample member and provider conversations to the AWS Bedrock Agent's memory system. This helps the agent learn user preferences, conversation patterns, and domain-specific knowledge.

## Purpose

Memory seeding serves several important purposes:

1. **Bootstrap Learning**: Provides initial training data for the memory system
2. **Preference Extraction**: Helps the agent learn user communication preferences
3. **Pattern Recognition**: Establishes common conversation patterns
4. **Context Building**: Creates semantic memory for future reference
5. **Testing**: Validates that memory storage and retrieval work correctly

## Script Details

### Configuration

- **Customer ID**: `user_001`
- **Memory Processing Wait**: 30 seconds (allows memory system to process and extract preferences)
- **Conversations**: 2 sample conversations with realistic healthcare scenarios

### Conversation 1: Member Eligibility and Benefits Inquiry

**Scenario**: A provider checks member eligibility and requests detailed benefit information

**Key Topics**:
- Member eligibility verification
- Coverage period validation
- Benefit details (copays, deductibles, OOP max)
- Prescription benefits
- Preventive care coverage

**Learning Outcomes**:
- Agent learns eligibility verification workflow
- Understands preference for detailed benefit breakdowns
- Recognizes member ID: M123456 as frequently accessed

### Conversation 2: Member Liability Calculations

**Scenario**: A provider requests liability calculations for multiple medical procedures

**Key Topics**:
- Specialist office visit ($250)
- Lab test ($500)
- MRI ($2,000)
- Surgery ($15,000)
- Deductible tracking
- Out-of-pocket maximum progression

**Learning Outcomes**:
- Agent learns step-by-step liability calculation approach
- Understands preference for detailed breakdowns
- Recognizes pattern of tracking deductible and OOP max
- Learns multi-procedure cost tracking methodology

## AWS API Usage

### Primary API: `invoke_agent`

The script uses the `bedrock-agent-runtime.invoke_agent()` method to store conversations:

```python
response = bedrock_agent_runtime.invoke_agent(
    agentId=AGENT_ID,
    agentAliasId=ALIAS_ID,
    sessionId=session_id,
    inputText=user_message,
    enableTrace=False,
    sessionState={
        'sessionAttributes': {
            'customerId': CUSTOMER_ID,
            'conversationTitle': conversation_title
        }
    }
)
```

### How Memory Storage Works

1. **Automatic Capture**: When you invoke the agent, AWS Bedrock automatically captures the conversation in memory
2. **Session Continuity**: Using the same `sessionId` maintains conversation context
3. **Session Attributes**: Custom attributes (like `customerId`) are stored with the conversation
4. **Streaming Response**: The agent's response is streamed back and automatically stored

### Memory Processing

After storing conversations, the script waits 30 seconds for the memory system to:

1. **Extract Summaries**: Create high-level conversation summaries (SESSION_SUMMARY)
2. **Identify Preferences**: Detect user preferences and patterns (USER_PREFERENCES)
3. **Build Semantic Index**: Create semantic embeddings for search (SEMANTIC_MEMORY)
4. **Store Patterns**: Recognize and store interaction patterns

## Usage

### Production Usage

```bash
# Ensure prerequisites are met
python3 create_agent.py
python3 03_create_memory.py

# Run memory seeding
python3 04_seed_memory.py
```

### Dry-Run Usage (No AWS Credentials Required)

```bash
# Test the script without AWS
python3 04_seed_memory_dryrun.py
```

## Expected Output

### Successful Execution

```
================================================================================
Benefits Member Liability Agent - Memory Seeding
================================================================================
Agent ID: AGENT123456
Alias ID: ALIAS123456
Memory ID: MEMORY123456
Customer ID: user_001
================================================================================

================================================================================
CONVERSATION 1: Member Eligibility and Benefits Inquiry
================================================================================

Turn 1 - User: Hi, I need to check eligibility for member M123456...
  ✓ Stored in memory

Turn 2 - User: The service date is March 15, 2024...
  ✓ Stored in memory

...

✅ Conversation stored successfully!

================================================================================
CONVERSATION 2: Member Liability Calculations
================================================================================

...

================================================================================
MEMORY PROCESSING
================================================================================

⏳ Waiting 30 seconds for memory system to process...
   10/30 seconds elapsed...
   20/30 seconds elapsed...
   30/30 seconds elapsed...

✅ Memory processing wait complete!

================================================================================
SEEDING SUMMARY
================================================================================
Customer ID: user_001
Conversations stored: 2/2

Conversation 1 (Eligibility): ✅ SUCCESS
Conversation 2 (Liability): ✅ SUCCESS

================================================================================
✅ SUCCESS: Memory seeding completed!
================================================================================
```

## Memory Learning Outcomes

After seeding, the agent's memory will contain:

### 1. Session Summaries

- Member eligibility verification workflow
- Liability calculation for multiple procedures
- Deductible and OOP max tracking patterns

### 2. User Preferences

- Customer prefers detailed benefit breakdowns
- Customer needs step-by-step liability calculations
- Customer tracks deductible and OOP max progression
- Frequently accessed member: M123456

### 3. Semantic Memory

- Eligibility verification patterns
- Liability calculation methodologies
- Benefit explanation approaches
- Multi-procedure cost tracking

## Verification

### Test Agent with Memory

```bash
python3 02_test_agent.py
```

Ask questions like:
- "What do you know about member M123456?"
- "How should I calculate liability for multiple procedures?"
- "What's the best way to explain benefits?"

The agent should demonstrate learned preferences and patterns.

### View Memory Contents

```bash
# Get memory details
aws bedrock-agent get-agent-memory \
  --agent-id <AGENT_ID> \
  --memory-id <MEMORY_ID>

# List all sessions
aws bedrock-agent-runtime list-agent-sessions \
  --agent-id <AGENT_ID> \
  --agent-alias-id <ALIAS_ID>

# Get specific session
aws bedrock-agent-runtime get-agent-session \
  --agent-id <AGENT_ID> \
  --agent-alias-id <ALIAS_ID> \
  --session-id <SESSION_ID>
```

## Error Handling

### Common Errors

#### 1. Agent Config Not Found

```
ERROR: agent_config.json not found. Run create_agent.py first.
```

**Solution**: Create the agent first:
```bash
python3 create_agent.py
```

#### 2. Memory Config Not Found

```
ERROR: memory_config.json not found. Run 03_create_memory.py first.
```

**Solution**: Create memory first:
```bash
python3 03_create_memory.py
```

#### 3. AWS Credentials Not Configured

```
ERROR: Unable to locate credentials
```

**Solution**: Configure AWS credentials:
```bash
aws configure
```

#### 4. Agent Not Prepared

```
ERROR: Agent is not in PREPARED state
```

**Solution**: Prepare the agent:
```bash
aws bedrock-agent prepare-agent --agent-id <AGENT_ID>
```

#### 5. Memory Not Associated

```
ERROR: Memory not associated with agent
```

**Solution**: Re-run memory creation script:
```bash
python3 03_create_memory.py
```

## Best Practices

### 1. Realistic Conversations

- Use realistic member IDs and scenarios
- Include natural conversation flow
- Add variety in questions and responses
- Cover common use cases

### 2. Diverse Topics

- Include different types of queries
- Cover various procedures and services
- Show different calculation scenarios
- Demonstrate edge cases

### 3. Preference Patterns

- Consistently demonstrate preferred communication style
- Show repeated patterns (e.g., always asking for detailed breakdowns)
- Include frequently accessed data (e.g., specific member IDs)

### 4. Wait Time

- Always wait 30 seconds after seeding
- This allows memory system to process
- Ensures preferences are extracted
- Validates semantic indexing completes

### 5. Verification

- Test agent after seeding
- Verify learned preferences
- Check semantic search works
- Validate session summaries

## Customization

### Adding More Conversations

```python
def create_conversation_3() -> List[Dict]:
    """Your custom conversation."""
    return [
        {
            'role': 'user',
            'content': 'Your user message'
        },
        {
            'role': 'assistant',
            'content': 'Agent response'
        },
        # ... more turns
    ]

# In seed_memory():
conversation_3 = create_conversation_3()
success_3 = store_conversation_in_memory(
    session_id=f"{CUSTOMER_ID}_custom_{timestamp + 2}",
    conversation=conversation_3,
    conversation_title="Custom Conversation"
)
```

### Changing Customer ID

```python
# At the top of the script
CUSTOMER_ID = 'your_custom_id'
```

### Adjusting Wait Time

```python
# At the top of the script
MEMORY_PROCESSING_WAIT = 60  # Wait 60 seconds instead of 30
```

### Adding Session Attributes

```python
sessionState={
    'sessionAttributes': {
        'customerId': CUSTOMER_ID,
        'conversationTitle': conversation_title,
        'department': 'claims',  # Custom attribute
        'priority': 'high'       # Custom attribute
    }
}
```

## Integration with Other Scripts

### Workflow Sequence

1. **Create Agent**: `python3 create_agent.py`
2. **Create Memory**: `python3 03_create_memory.py`
3. **Seed Memory**: `python3 04_seed_memory.py` ← This script
4. **Test Agent**: `python3 02_test_agent.py`

### Data Flow

```
create_agent.py
    ↓
agent_config.json → 04_seed_memory.py
    ↓
03_create_memory.py
    ↓
memory_config.json → 04_seed_memory.py
    ↓
04_seed_memory.py (stores conversations)
    ↓
Agent Memory (SESSION_SUMMARY, USER_PREFERENCES, SEMANTIC_MEMORY)
    ↓
02_test_agent.py (uses learned preferences)
```

## Performance Considerations

### Memory Storage Costs

- **Storage**: ~$0.10-0.50/month for typical usage
- **Retrieval**: ~$0.01-0.05 per 1000 retrievals
- **Processing**: Included in agent invocation costs

### Optimization Tips

1. **Batch Conversations**: Store multiple conversations in one session
2. **Efficient Sessions**: Use meaningful session IDs for organization
3. **Attribute Indexing**: Use session attributes for filtering
4. **Regular Cleanup**: Remove old sessions if not needed

## Troubleshooting

### Memory Not Learning Preferences

**Symptoms**: Agent doesn't demonstrate learned preferences

**Solutions**:
1. Increase wait time to 60 seconds
2. Verify memory is associated with agent
3. Check memory strategies are enabled
4. Review CloudWatch logs for errors

### Conversations Not Stored

**Symptoms**: No sessions appear in memory

**Solutions**:
1. Verify agent is in PREPARED state
2. Check IAM permissions for invoke_agent
3. Ensure session IDs are unique
4. Review agent configuration

### Semantic Search Not Working

**Symptoms**: Can't find relevant past conversations

**Solutions**:
1. Verify SEMANTIC_MEMORY strategy is enabled
2. Wait longer for indexing to complete
3. Check memory configuration
4. Test with more diverse conversations

## Security Considerations

### Data Privacy

- **PII Handling**: Be careful with real member data
- **Test Data**: Use synthetic data for testing
- **Data Retention**: Configure appropriate retention periods
- **Access Control**: Restrict access to memory contents

### IAM Permissions

Required permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock:GetAgentMemory",
        "bedrock:ListAgentSessions"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:agent/*",
        "arn:aws:bedrock:*:*:agent-memory/*"
      ]
    }
  ]
}
```

## Files Generated

- `04_seed_memory.py` - Production memory seeding script
- `04_seed_memory_dryrun.py` - Dry-run version for testing
- `04_SEED_MEMORY_DOCUMENTATION.md` - This documentation

## Next Steps

After seeding memory:

1. **Test Agent**: Run `02_test_agent.py` to verify learned preferences
2. **Monitor Usage**: Check CloudWatch logs for memory retrieval
3. **Iterate**: Add more conversations based on real usage patterns
4. **Optimize**: Adjust wait times and conversation content
5. **Production**: Deploy to production environment

## Conclusion

The memory seeding script is a crucial step in preparing your Bedrock Agent for production use. It provides initial training data that helps the agent learn user preferences, conversation patterns, and domain knowledge. By following this documentation, you can effectively seed your agent's memory and verify that it's learning correctly.
