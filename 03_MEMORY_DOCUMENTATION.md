# Agent Memory Setup Documentation

## Overview

The `03_create_memory.py` script sets up memory for the Benefits Member Liability Agent, enabling it to store and recall member interactions, preferences, and conversation history.

## Memory Configuration

### Memory Name
`member_liability_memory`

### Description
Stores member and provider interactions, preferences, and history

### Memory Strategies

The script configures all three AWS Bedrock Agent memory strategies:

#### 1. SESSION_SUMMARY (Summary Strategy)
**Purpose**: Maintains high-level conversation summaries

**How it works**:
- Automatically summarizes long conversations
- Reduces token usage by condensing context
- Provides quick context for new sessions

**Use cases**:
- Member calls back about previous inquiry
- Long multi-turn conversations
- Reducing context window usage

**Example**:
```
Original conversation (500 tokens):
"I need to check eligibility for member M123456..."
[Long back-and-forth discussion]

Summary (50 tokens):
"Verified eligibility for M123456, calculated $150 liability 
for primary care visit, explained deductible status."
```

#### 2. USER_PREFERENCES (Preferences Strategy)
**Purpose**: Stores user preferences and settings

**How it works**:
- Learns from user interactions
- Stores explicit preferences
- Adapts responses based on history

**Use cases**:
- Remembering frequently accessed member IDs
- Preferred response format (detailed vs. brief)
- Communication style preferences
- Calculation method preferences

**Example stored preferences**:
```json
{
  "preferred_members": ["M123456", "M789012"],
  "response_style": "detailed_breakdown",
  "always_show_deductible": true,
  "preferred_date_format": "YYYY-MM-DD"
}
```

#### 3. SEMANTIC_MEMORY (Semantic Strategy)
**Purpose**: Enables semantic search across conversation history

**How it works**:
- Stores conversation embeddings
- Enables similarity search
- Retrieves relevant past interactions

**Use cases**:
- Finding similar past cases
- "Have we seen this before?"
- Learning from historical patterns
- Improving accuracy with context

**Example**:
```
Current query: "Member with high deductible and copay"

Semantic search finds similar past case:
"3 months ago: Member M789012 with $1000 deductible 
and $50 copay, calculated liability of $275"
```

## Usage

### Basic Usage

```bash
python3 03_create_memory.py
```

### Prerequisites

1. **Agent must be created**:
   ```bash
   python3 create_agent.py
   ```

2. **agent_config.json must exist** with agent_id

3. **AWS credentials configured**:
   ```bash
   aws configure
   ```

4. **IAM permissions** for:
   - `bedrock:CreateAgentMemory`
   - `bedrock:UpdateAgent`
   - `bedrock:PrepareAgent`
   - `bedrock:ListAgentMemories`

## Output

### Success Output

```
================================================================================
Benefits Member Liability Agent - Memory Setup
================================================================================

Creating Agent Memory
================================================================================
Memory Name: member_liability_memory
Description: Stores member and provider interactions, preferences, and history
Agent ID: AGENT123456
================================================================================

📝 Creating memory with all three strategies...
   - Summary: Conversation summaries
   - Preferences: User preferences and settings
   - Semantic: Semantic search capability

✅ Memory created successfully!
   Memory ID: MEMORY789012
   Memory ARN: arn:aws:bedrock:us-east-1:123456789012:agent-memory/MEMORY789012

✅ Memory configuration saved to: memory_config.json

🔗 Associating memory with agent...
✅ Memory associated with agent successfully

🔄 Preparing agent with new memory configuration...
✅ Agent prepared with status: PREPARED

================================================================================
MEMORY CONFIGURATION SUMMARY
================================================================================
Memory ID: MEMORY789012
Memory Name: member_liability_memory
Description: Stores member and provider interactions, preferences, and history
Agent ID: AGENT123456

Enabled Memory Strategies:
  ✓ Session Summary
  ✓ User Preferences
  ✓ Semantic Memory

================================================================================
✅ SUCCESS: Memory setup completed!
================================================================================
```

### Generated Files

#### memory_config.json

```json
{
  "memory_id": "MEMORY789012",
  "memory_arn": "arn:aws:bedrock:us-east-1:123456789012:agent-memory/MEMORY789012",
  "memory_name": "member_liability_memory",
  "description": "Stores member and provider interactions, preferences, and history",
  "agent_id": "AGENT123456",
  "enabled_strategies": [
    "SESSION_SUMMARY",
    "USER_PREFERENCES",
    "SEMANTIC_MEMORY"
  ],
  "created_at": "2024-03-15T10:30:00",
  "existing": false
}
```

## Memory Behavior

### How Memory is Used

1. **During Conversation**:
   - Agent automatically stores conversation context
   - Summaries are generated after each session
   - Preferences are learned from interactions
   - Semantic embeddings are created for search

2. **Between Sessions**:
   - Memory persists for 30 days (configurable)
   - Can be retrieved in new sessions
   - Enables continuity across conversations

3. **For Retrieval**:
   - Agent automatically accesses relevant memories
   - No explicit memory queries needed
   - Transparent to the user

### Memory Retention

- **Default**: 30 days
- **Configurable**: Can be adjusted in script
- **Automatic cleanup**: Old memories are purged
- **Manual deletion**: Can be deleted via API

## Testing Memory

### Test Conversation Flow

```python
# Session 1: Initial interaction
python3 02_test_agent.py

Query: "Check eligibility for member M123456"
Response: [Eligibility details]
# Memory stores: Member ID, eligibility status, conversation summary

# Session 2: Follow-up (new session ID)
Query: "What was the status of that member I asked about?"
Response: "You previously asked about member M123456, who is eligible..."
# Memory retrieves: Previous conversation context
```

### Verify Memory Storage

```bash
# View memory contents
aws bedrock-agent get-agent-memory \
  --agent-id AGENT123456 \
  --memory-id MEMORY789012

# List all memories for agent
aws bedrock-agent list-agent-memories \
  --agent-id AGENT123456
```

## API Validation

### boto3 Methods Used

#### 1. create_agent_memory

```python
response = bedrock_agent_client.create_agent_memory(
    agentId='string',           # Required
    memoryName='string',        # Required
    description='string',       # Optional
    memoryConfiguration={       # Required
        'enabledMemoryTypes': [
            'SESSION_SUMMARY',
            'USER_PREFERENCES',
            'SEMANTIC_MEMORY'
        ]
    }
)
```

**Returns**:
```python
{
    'memoryId': 'string',
    'memoryArn': 'string'
}
```

#### 2. update_agent

```python
response = bedrock_agent_client.update_agent(
    agentId='string',
    memoryConfiguration={
        'enabledMemoryTypes': [...],
        'storageDays': 30
    }
)
```

#### 3. prepare_agent

```python
response = bedrock_agent_client.prepare_agent(
    agentId='string'
)
```

**Returns**:
```python
{
    'agentStatus': 'PREPARED'|'FAILED'|'CREATING'|'UPDATING'
}
```

#### 4. list_agent_memories

```python
response = bedrock_agent_client.list_agent_memories(
    agentId='string',
    maxResults=10,
    nextToken='string'
)
```

**Returns**:
```python
{
    'memories': [
        {
            'memoryId': 'string',
            'memoryName': 'string',
            'memoryArn': 'string',
            'description': 'string'
        }
    ],
    'nextToken': 'string'
}
```

## Error Handling

### Common Errors

#### 1. Agent Not Found

```
❌ ERROR: Agent AGENT123456 not found
```

**Solution**: Run `create_agent.py` first

#### 2. Memory Already Exists

```
⚠️  WARNING: Memory 'member_liability_memory' already exists
```

**Behavior**: Script retrieves existing memory ID and continues

#### 3. Access Denied

```
❌ ERROR: Access denied
```

**Solution**: Check IAM permissions:
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:CreateAgentMemory",
    "bedrock:UpdateAgent",
    "bedrock:PrepareAgent",
    "bedrock:ListAgentMemories"
  ],
  "Resource": "*"
}
```

#### 4. agent_config.json Not Found

```
ERROR: agent_config.json not found. Run create_agent.py first.
```

**Solution**: Create agent first

## Memory Best Practices

### 1. Memory Naming

- Use descriptive names
- Include purpose in name
- Follow naming conventions

### 2. Memory Strategies

- Enable all three for best results
- Summary: Always recommended
- Preferences: For personalization
- Semantic: For complex queries

### 3. Retention Period

- Default: 30 days
- Adjust based on use case
- Consider compliance requirements
- Balance cost vs. utility

### 4. Memory Management

- Monitor memory usage
- Clean up old memories
- Test memory retrieval
- Validate accuracy

## Integration with Agent

### How Agent Uses Memory

1. **Automatic Context**:
   - Agent automatically accesses memory
   - No explicit memory queries needed
   - Transparent to user

2. **Response Enhancement**:
   - Personalized responses
   - Context-aware answers
   - Improved accuracy

3. **Conversation Continuity**:
   - Remembers past interactions
   - Maintains context across sessions
   - Reduces repetition

### Example Conversation with Memory

```
Session 1:
User: "Check eligibility for M123456"
Agent: "Member M123456 is eligible..."
[Memory stores: M123456, eligibility check, date]

Session 2 (next day):
User: "What was the liability for that member?"
Agent: "For member M123456 that you asked about yesterday, 
       the calculated liability was $150..."
[Memory retrieved: Previous M123456 interaction]

Session 3:
User: "Check another member"
Agent: "Would you like me to check eligibility similar to 
       how I did for M123456?"
[Memory suggests: Similar workflow preference]
```

## Monitoring Memory

### CloudWatch Metrics

Monitor these metrics:
- Memory storage usage
- Memory retrieval latency
- Memory hit rate
- Memory errors

### CloudWatch Logs

Check logs for:
- Memory creation events
- Memory access patterns
- Memory errors
- Memory updates

## Cost Considerations

### Memory Costs

- **Storage**: Per GB per month
- **Retrieval**: Per request
- **Retention**: Based on storage days

### Cost Optimization

1. Set appropriate retention period
2. Clean up unused memories
3. Monitor storage usage
4. Use summary strategy to reduce tokens

## Troubleshooting

### Memory Not Working

1. **Check memory is created**:
   ```bash
   aws bedrock-agent list-agent-memories --agent-id AGENT123456
   ```

2. **Verify agent is prepared**:
   ```bash
   aws bedrock-agent get-agent --agent-id AGENT123456
   ```

3. **Check memory configuration**:
   ```bash
   cat memory_config.json
   ```

4. **Test memory retrieval**:
   ```bash
   python3 02_test_agent.py
   ```

### Memory Not Persisting

- Check retention period
- Verify memory is associated with agent
- Check CloudWatch logs for errors
- Ensure agent is in PREPARED state

## Next Steps

After creating memory:

1. **Test Memory**:
   ```bash
   python3 02_test_agent.py
   ```

2. **Verify Storage**:
   - Have multiple conversations
   - Check memory retrieval
   - Validate preferences

3. **Monitor Usage**:
   - Check CloudWatch metrics
   - Review memory logs
   - Monitor costs

4. **Optimize**:
   - Adjust retention period
   - Fine-tune strategies
   - Clean up old memories

## References

- **AWS Bedrock Agent Memory**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-memory.html
- **boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent.html
- **Memory Best Practices**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-memory-best-practices.html

---

**Script**: `03_create_memory.py`
**Configuration**: `memory_config.json`
**Status**: Ready for deployment
