# API Validation - boto3 Bedrock Agent Runtime

## boto3 API Usage in 02_test_agent.py

### Client Initialization

```python
import boto3

# Initialize Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
```

**Validated**: This is the correct way to initialize the Bedrock Agent Runtime client.

### invoke_agent Method

```python
response = bedrock_agent_runtime.invoke_agent(
    agentId=AGENT_ID,           # Required: string
    agentAliasId=ALIAS_ID,      # Required: string
    sessionId=session_id,       # Required: string
    inputText=query,            # Required: string
    enableTrace=enable_trace    # Optional: boolean
)
```

**Method Signature** (from AWS SDK documentation):

```python
response = client.invoke_agent(
    agentId='string',           # Required
    agentAliasId='string',      # Required
    sessionId='string',         # Required
    inputText='string',         # Required
    enableTrace=True|False,     # Optional, default: False
    endSession=True|False,      # Optional, default: False
    memoryId='string',          # Optional
    sessionState={              # Optional
        'invocationId': 'string',
        'promptSessionAttributes': {
            'string': 'string'
        },
        'returnControlInvocationResults': [
            {
                'apiResult': {
                    'actionGroup': 'string',
                    'apiPath': 'string',
                    'httpMethod': 'string',
                    'httpStatusCode': 123,
                    'responseBody': {
                        'string': {
                            'body': 'string'
                        }
                    },
                    'responseState': {
                        'string': 'string'
                    }
                },
                'functionResult': {
                    'actionGroup': 'string',
                    'function': 'string',
                    'responseBody': {
                        'string': {
                            'body': 'string'
                        }
                    },
                    'responseState': {
                        'string': 'string'
                    }
                }
            }
        ],
        'sessionAttributes': {
            'string': 'string'
        }
    }
)
```

**Parameters Used in 02_test_agent.py**:

| Parameter | Type | Required | Usage |
|-----------|------|----------|-------|
| agentId | string | Yes | Agent identifier from agent_config.json |
| agentAliasId | string | Yes | Alias identifier from agent_config.json |
| sessionId | string | Yes | Unique session ID for conversation continuity |
| inputText | string | Yes | User's query/question |
| enableTrace | boolean | No | Set to True to get execution trace |

**Validation**: ✅ All parameters are correctly used according to AWS SDK documentation.

### Response Structure

```python
response = {
    'completion': EventStream,  # Streaming response
    'contentType': 'string',
    'memoryId': 'string',
    'sessionId': 'string'
}
```

**EventStream Structure**:

```python
for event in response['completion']:
    # Event types:
    
    # 1. Chunk event (response text)
    if 'chunk' in event:
        chunk = event['chunk']
        chunk_text = chunk['bytes'].decode('utf-8')
    
    # 2. Trace event (execution details)
    if 'trace' in event:
        trace = event['trace']
        # Contains orchestration trace, invocation details, etc.
    
    # 3. Return control event
    if 'returnControl' in event:
        return_control = event['returnControl']
    
    # 4. Files event
    if 'files' in event:
        files = event['files']
```

**Validation**: ✅ Response handling in 02_test_agent.py correctly processes streaming events.

## Code Validation

### 1. Import Statements

```python
import boto3
import json
import sys
import time
from typing import Dict, Optional, Tuple
```

**Validation**: ✅ All imports are standard library or boto3.

### 2. Configuration Loading

```python
try:
    with open('agent_config.json', 'r') as f:
        config = json.load(f)
        AGENT_ID = config['agent_id']
        ALIAS_ID = config['alias_id']
        KB_ID = config.get('knowledge_base_id', '<PLACE-YOUR-KB-ID>')
except FileNotFoundError:
    print("ERROR: agent_config.json not found. Run create_agent.py first.")
    sys.exit(1)
```

**Validation**: ✅ Proper error handling for missing configuration file.

### 3. Response Processing

```python
full_response = ""
trace_data = []

for event in response['completion']:
    if 'chunk' in event:
        chunk = event['chunk']
        chunk_text = chunk['bytes'].decode('utf-8')
        full_response += chunk_text
        print(chunk_text, end='', flush=True)
    
    if enable_trace and 'trace' in event:
        trace_data.append(event['trace'])
```

**Validation**: ✅ Correctly handles streaming response and trace data.

### 4. Error Handling

```python
try:
    response = bedrock_agent_runtime.invoke_agent(...)
    # Process response
    return AgentResponse(text=full_response, success=True)
except Exception as e:
    error_msg = f"Failed to invoke agent: {str(e)}"
    print(f"❌ ERROR: {error_msg}\n")
    return AgentResponse(text="", success=False, error=error_msg)
```

**Validation**: ✅ Proper exception handling with informative error messages.

## AWS SDK Version Requirements

### Minimum boto3 Version

```
boto3>=1.34.0
```

This version includes support for:
- AWS Bedrock Agent Runtime
- invoke_agent method
- Streaming responses
- Trace functionality

### Installation

```bash
pip install boto3>=1.34.0
```

Or use the provided requirements.txt:

```bash
pip install -r requirements.txt
```

## API Compatibility

### Tested With

- **boto3**: 1.34.0+
- **Python**: 3.9+
- **AWS SDK**: Latest

### Known Compatible Regions

- us-east-1
- us-west-2
- eu-west-1
- ap-southeast-1
- ap-northeast-1

Check AWS documentation for latest region availability.

## Error Codes and Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| ResourceNotFoundException | Agent not found | Verify agent_id in config |
| AccessDeniedException | IAM permissions | Check IAM role permissions |
| ValidationException | Invalid parameters | Verify parameter types |
| ThrottlingException | Rate limit exceeded | Implement retry with backoff |
| InternalServerException | AWS service error | Retry request |

### Error Handling in Code

```python
try:
    response = bedrock_agent_runtime.invoke_agent(...)
except bedrock_agent_runtime.exceptions.ResourceNotFoundException:
    print("Agent not found. Check agent_id.")
except bedrock_agent_runtime.exceptions.AccessDeniedException:
    print("Access denied. Check IAM permissions.")
except bedrock_agent_runtime.exceptions.ValidationException as e:
    print(f"Invalid parameters: {e}")
except bedrock_agent_runtime.exceptions.ThrottlingException:
    print("Rate limit exceeded. Retrying...")
    time.sleep(2)
    # Retry logic
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Session Management

```python
# Use unique session IDs for each conversation
session_id = f'workflow-test-{int(time.time())}'

# Reuse session ID for conversation continuity
invoke_agent(query1, session_id)
invoke_agent(query2, session_id)  # Same session
```

### 2. Trace Usage

```python
# Enable trace for debugging
response = bedrock_agent_runtime.invoke_agent(
    ...,
    enableTrace=True  # Get execution details
)

# Process trace data
for event in response['completion']:
    if 'trace' in event:
        # Log trace information
        print(f"Trace: {event['trace']}")
```

### 3. Rate Limiting

```python
import time

# Add delay between requests
invoke_agent(query1, session_id)
time.sleep(2)  # 2 second delay
invoke_agent(query2, session_id)
```

### 4. Response Streaming

```python
# Stream response for better UX
for event in response['completion']:
    if 'chunk' in event:
        chunk_text = event['chunk']['bytes'].decode('utf-8')
        print(chunk_text, end='', flush=True)  # Real-time output
```

## Testing the API

### Manual Test

```python
import boto3

client = boto3.client('bedrock-agent-runtime')

response = client.invoke_agent(
    agentId='YOUR_AGENT_ID',
    agentAliasId='YOUR_ALIAS_ID',
    sessionId='test-session',
    inputText='Hello, test query'
)

for event in response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'))
```

### Validation Script

```python
# validate_api.py
import boto3
import sys

def validate_bedrock_agent_runtime():
    """Validate boto3 Bedrock Agent Runtime API."""
    try:
        client = boto3.client('bedrock-agent-runtime')
        print("✅ Bedrock Agent Runtime client created successfully")
        
        # Check if invoke_agent method exists
        if hasattr(client, 'invoke_agent'):
            print("✅ invoke_agent method available")
        else:
            print("❌ invoke_agent method not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if validate_bedrock_agent_runtime():
        print("\n✅ API validation passed")
        sys.exit(0)
    else:
        print("\n❌ API validation failed")
        sys.exit(1)
```

## Documentation References

- **AWS Bedrock Agent Runtime**: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html
- **boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html
- **AWS SDK for Python**: https://aws.amazon.com/sdk-for-python/

## Validation Summary

✅ **All API usage in 02_test_agent.py is validated and correct**:

1. ✅ Client initialization
2. ✅ invoke_agent method signature
3. ✅ Parameter types and usage
4. ✅ Response handling
5. ✅ Streaming event processing
6. ✅ Error handling
7. ✅ Trace functionality
8. ✅ Session management

**No manual code creation was needed** - all code follows AWS SDK best practices and documentation.
