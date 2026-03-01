#!/usr/bin/env python3
"""
Create Memory for Benefits Member Liability Agent
This script sets up agent memory to store member and provider interactions,
preferences, and history.

Memory Strategies:
- Summary: Maintains conversation summaries
- Preferences: Stores user preferences and settings
- Semantic: Enables semantic search across conversation history

Usage:
    python3 03_create_memory.py
"""

import boto3
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Configuration
MEMORY_NAME = 'member_liability_memory'
MEMORY_DESCRIPTION = 'Stores member and provider interactions, preferences, and history'
MEMORY_CONFIG_FILE = 'memory_config.json'

# Load agent configuration
try:
    with open('agent_config.json', 'r') as f:
        agent_config = json.load(f)
        AGENT_ID = agent_config['agent_id']
except FileNotFoundError:
    print("ERROR: agent_config.json not found. Run create_agent.py first.")
    sys.exit(1)
except KeyError:
    print("ERROR: agent_id not found in agent_config.json")
    sys.exit(1)

# Initialize Bedrock Agent client
bedrock_agent_client = boto3.client('bedrock-agent')


def create_agent_memory() -> Dict:
    """
    Create agent memory with all three memory strategies.
    
    Memory Strategies:
    1. Summary: Maintains high-level conversation summaries
    2. Preferences: Stores user preferences and settings
    3. Semantic: Enables semantic search across history
    
    Returns:
        Dictionary containing memory ID and configuration
    """
    print("="*80)
    print("Creating Agent Memory")
    print("="*80)
    print(f"Memory Name: {MEMORY_NAME}")
    print(f"Description: {MEMORY_DESCRIPTION}")
    print(f"Agent ID: {AGENT_ID}")
    print("="*80)
    
    try:
        print("\n📝 Creating memory with all three strategies...")
        print("   - Summary: Conversation summaries")
        print("   - Preferences: User preferences and settings")
        print("   - Semantic: Semantic search capability")
        
        # Create memory
        # Note: AWS Bedrock Agent Memory API
        # Reference: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_CreateAgentMemory.html
        
        response = bedrock_agent_client.create_agent_memory(
            agentId=AGENT_ID,
            memoryName=MEMORY_NAME,
            description=MEMORY_DESCRIPTION,
            memoryConfiguration={
                'enabledMemoryTypes': [
                    'SESSION_SUMMARY',    # Summary strategy
                    'USER_PREFERENCES',   # Preferences strategy  
                    'SEMANTIC_MEMORY'     # Semantic strategy
                ]
            }
        )
        
        memory_id = response['memoryId']
        memory_arn = response.get('memoryArn', f'arn:aws:bedrock:region:account:agent-memory/{memory_id}')
        
        print(f"\n✅ Memory created successfully!")
        print(f"   Memory ID: {memory_id}")
        print(f"   Memory ARN: {memory_arn}")
        
        return {
            'memory_id': memory_id,
            'memory_arn': memory_arn,
            'memory_name': MEMORY_NAME,
            'description': MEMORY_DESCRIPTION,
            'agent_id': AGENT_ID,
            'enabled_strategies': [
                'SESSION_SUMMARY',
                'USER_PREFERENCES',
                'SEMANTIC_MEMORY'
            ]
        }
        
    except bedrock_agent_client.exceptions.ResourceNotFoundException:
        print(f"\n❌ ERROR: Agent {AGENT_ID} not found")
        print("   Please ensure the agent exists and is properly configured")
        sys.exit(1)
        
    except bedrock_agent_client.exceptions.ConflictException:
        print(f"\n⚠️  WARNING: Memory '{MEMORY_NAME}' already exists for this agent")
        print("   Retrieving existing memory configuration...")
        
        # List existing memories to get the ID
        try:
            list_response = bedrock_agent_client.list_agent_memories(
                agentId=AGENT_ID
            )
            
            # Find the memory by name
            for memory in list_response.get('memories', []):
                if memory.get('memoryName') == MEMORY_NAME:
                    memory_id = memory['memoryId']
                    memory_arn = memory.get('memoryArn', '')
                    
                    print(f"✅ Using existing memory:")
                    print(f"   Memory ID: {memory_id}")
                    print(f"   Memory ARN: {memory_arn}")
                    
                    return {
                        'memory_id': memory_id,
                        'memory_arn': memory_arn,
                        'memory_name': MEMORY_NAME,
                        'description': MEMORY_DESCRIPTION,
                        'agent_id': AGENT_ID,
                        'enabled_strategies': [
                            'SESSION_SUMMARY',
                            'USER_PREFERENCES',
                            'SEMANTIC_MEMORY'
                        ],
                        'existing': True
                    }
            
            print("❌ ERROR: Memory exists but could not be retrieved")
            sys.exit(1)
            
        except Exception as e:
            print(f"❌ ERROR: Failed to retrieve existing memory: {str(e)}")
            sys.exit(1)
    
    except bedrock_agent_client.exceptions.AccessDeniedException:
        print("\n❌ ERROR: Access denied")
        print("   Please check IAM permissions for bedrock:CreateAgentMemory")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create memory: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify AWS credentials are configured")
        print("2. Check IAM permissions for Bedrock Agent Memory")
        print("3. Ensure agent exists and is in PREPARED state")
        print("4. Verify AWS region is correct")
        sys.exit(1)


def save_memory_config(memory_info: Dict) -> None:
    """
    Save memory configuration to JSON file.
    
    Args:
        memory_info: Dictionary containing memory details
    """
    config = {
        'memory_id': memory_info['memory_id'],
        'memory_arn': memory_info.get('memory_arn', ''),
        'memory_name': memory_info['memory_name'],
        'description': memory_info['description'],
        'agent_id': memory_info['agent_id'],
        'enabled_strategies': memory_info['enabled_strategies'],
        'created_at': datetime.now().isoformat(),
        'existing': memory_info.get('existing', False)
    }
    
    with open(MEMORY_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Memory configuration saved to: {MEMORY_CONFIG_FILE}")


def associate_memory_with_agent(memory_id: str) -> None:
    """
    Associate the memory with the agent.
    
    Args:
        memory_id: The memory identifier
    """
    print(f"\n🔗 Associating memory with agent...")
    
    try:
        # Update agent to use the memory
        bedrock_agent_client.update_agent(
            agentId=AGENT_ID,
            memoryConfiguration={
                'enabledMemoryTypes': [
                    'SESSION_SUMMARY',
                    'USER_PREFERENCES',
                    'SEMANTIC_MEMORY'
                ],
                'storageDays': 30  # Retain memory for 30 days
            }
        )
        
        print("✅ Memory associated with agent successfully")
        
        # Prepare the agent to apply changes
        print("\n🔄 Preparing agent with new memory configuration...")
        prepare_response = bedrock_agent_client.prepare_agent(
            agentId=AGENT_ID
        )
        
        status = prepare_response.get('agentStatus', 'UNKNOWN')
        print(f"✅ Agent prepared with status: {status}")
        
    except Exception as e:
        print(f"⚠️  WARNING: Could not associate memory with agent: {str(e)}")
        print("   You may need to manually configure memory in the AWS Console")


def display_memory_info(memory_info: Dict) -> None:
    """
    Display memory configuration information.
    
    Args:
        memory_info: Dictionary containing memory details
    """
    print("\n" + "="*80)
    print("MEMORY CONFIGURATION SUMMARY")
    print("="*80)
    print(f"Memory ID: {memory_info['memory_id']}")
    print(f"Memory Name: {memory_info['memory_name']}")
    print(f"Description: {memory_info['description']}")
    print(f"Agent ID: {memory_info['agent_id']}")
    print(f"\nEnabled Memory Strategies:")
    for strategy in memory_info['enabled_strategies']:
        strategy_name = strategy.replace('_', ' ').title()
        print(f"  ✓ {strategy_name}")
    
    print("\n" + "="*80)
    print("MEMORY STRATEGY DETAILS")
    print("="*80)
    
    print("\n1. SESSION_SUMMARY (Summary Strategy)")
    print("   Purpose: Maintains high-level conversation summaries")
    print("   Use Case: Quick context retrieval for ongoing conversations")
    print("   Benefits:")
    print("   - Reduces token usage by summarizing long conversations")
    print("   - Provides quick context for new sessions")
    print("   - Maintains conversation continuity")
    
    print("\n2. USER_PREFERENCES (Preferences Strategy)")
    print("   Purpose: Stores user preferences and settings")
    print("   Use Case: Personalized responses based on user history")
    print("   Benefits:")
    print("   - Remembers member communication preferences")
    print("   - Stores frequently accessed member IDs")
    print("   - Tracks preferred calculation methods")
    
    print("\n3. SEMANTIC_MEMORY (Semantic Strategy)")
    print("   Purpose: Enables semantic search across conversation history")
    print("   Use Case: Find relevant past interactions")
    print("   Benefits:")
    print("   - Search by meaning, not just keywords")
    print("   - Retrieve similar past cases")
    print("   - Improve response accuracy with historical context")
    
    print("\n" + "="*80)


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("Benefits Member Liability Agent - Memory Setup")
    print("="*80)
    
    try:
        # Create memory
        memory_info = create_agent_memory()
        
        # Save configuration
        save_memory_config(memory_info)
        
        # Associate with agent (if not existing)
        if not memory_info.get('existing', False):
            associate_memory_with_agent(memory_info['memory_id'])
        else:
            print("\n✓ Memory already associated with agent")
        
        # Display information
        display_memory_info(memory_info)
        
        print("\n" + "="*80)
        print("✅ SUCCESS: Memory setup completed!")
        print("="*80)
        
        print("\nNext steps:")
        print("1. Test the agent with memory enabled")
        print("2. Verify memory is storing conversation history")
        print("3. Check that preferences are being saved")
        print("4. Test semantic search functionality")
        
        print("\nTo test memory:")
        print("  python3 02_test_agent.py")
        print("\nTo view memory contents:")
        print("  aws bedrock-agent get-agent-memory \\")
        print(f"    --agent-id {AGENT_ID} \\")
        print(f"    --memory-id {memory_info['memory_id']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
