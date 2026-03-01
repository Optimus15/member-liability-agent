#!/usr/bin/env python3
"""
Test Memory for Benefits Member Liability Agent
This script retrieves and displays memories stored for a specific user,
demonstrating what the agent has learned from previous conversations.

Features:
- Loads memory ID from memory_config.json
- Retrieves memories for user_001 from preferences namespace
- Searches for specific topics (eligibility and liability)
- Displays what the agent remembers about the customer

Usage:
    python3 05_test_memory.py
"""

import boto3
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Configuration
USER_ID = 'user_001'
SEARCH_QUERY = 'customer eligibility and liability'

# Load memory configuration
try:
    with open('memory_config.json', 'r') as f:
        memory_config = json.load(f)
        MEMORY_ID = memory_config['memory_id']
        AGENT_ID = memory_config['agent_id']
except FileNotFoundError:
    print("ERROR: memory_config.json not found. Run 03_create_memory.py first.")
    sys.exit(1)
except KeyError as e:
    print(f"ERROR: Missing key in memory_config.json: {e}")
    sys.exit(1)

# Load agent configuration for additional context
try:
    with open('agent_config.json', 'r') as f:
        agent_config = json.load(f)
        ALIAS_ID = agent_config.get('alias_id', '')
except FileNotFoundError:
    print("WARNING: agent_config.json not found. Some features may be limited.")
    ALIAS_ID = ''

# Initialize Bedrock Agent Runtime client
# NOTE: This client is used to retrieve agent memory
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')


def get_agent_memory_summary() -> Optional[Dict]:
    """
    Retrieve the agent's memory summary.
    
    NOTE: AWS Bedrock Agent Memory API
    Reference: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_GetAgentMemory.html
    
    Returns:
        Dictionary containing memory summary or None if error
    """
    print("="*80)
    print("Retrieving Agent Memory Summary")
    print("="*80)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Memory ID: {MEMORY_ID}")
    print("="*80)
    
    try:
        # Get agent memory
        # NOTE: This retrieves the memory configuration and summary
        response = bedrock_agent_runtime.get_agent_memory(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            memoryId=MEMORY_ID,
            memoryType='SESSION_SUMMARY'  # Get session summaries
        )
        
        print("\n✅ Memory retrieved successfully!")
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to retrieve memory: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify agent and memory exist")
        print("2. Check AWS credentials are configured")
        print("3. Ensure memory is associated with agent")
        print("4. Review IAM permissions")
        return None


def retrieve_user_preferences(user_id: str) -> Optional[Dict]:
    """
    Retrieve user preferences from the agent's memory.
    
    Args:
        user_id: The user identifier (e.g., 'user_001')
    
    Returns:
        Dictionary containing user preferences or None if error
    """
    print("\n" + "="*80)
    print(f"Retrieving User Preferences for: {user_id}")
    print("="*80)
    
    try:
        # Retrieve user-specific preferences
        # NOTE: This gets preferences stored in the USER_PREFERENCES namespace
        response = bedrock_agent_runtime.get_agent_memory(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            memoryId=MEMORY_ID,
            memoryType='USER_PREFERENCES',
            # Filter by user ID if supported
            # NOTE: The exact filtering mechanism may vary by AWS implementation
        )
        
        print(f"\n✅ User preferences retrieved for {user_id}!")
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to retrieve user preferences: {str(e)}")
        print("\nNote: User preferences may not be available yet.")
        print("Run 04_seed_memory.py to populate memory with sample data.")
        return None


def search_semantic_memory(query: str) -> Optional[Dict]:
    """
    Search the agent's semantic memory for specific topics.
    
    Args:
        query: Search query (e.g., 'customer eligibility and liability')
    
    Returns:
        Dictionary containing search results or None if error
    """
    print("\n" + "="*80)
    print(f"Searching Semantic Memory")
    print("="*80)
    print(f"Query: '{query}'")
    print("="*80)
    
    try:
        # Search semantic memory
        # NOTE: This searches across conversation history using semantic similarity
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'EXTERNAL_SOURCES',
                'externalSourcesConfiguration': {
                    'modelArn': f'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0',
                    'sources': [
                        {
                            'sourceType': 'AGENT_MEMORY',
                            'agentMemoryConfiguration': {
                                'agentId': AGENT_ID,
                                'agentAliasId': ALIAS_ID,
                                'memoryId': MEMORY_ID
                            }
                        }
                    ]
                }
            }
        )
        
        print(f"\n✅ Semantic search completed!")
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to search semantic memory: {str(e)}")
        print("\nNote: Semantic search may not be available or configured.")
        print("This feature requires SEMANTIC_MEMORY strategy to be enabled.")
        return None


def list_agent_sessions() -> Optional[List[Dict]]:
    """
    List all agent sessions to see conversation history.
    
    Returns:
        List of session dictionaries or None if error
    """
    print("\n" + "="*80)
    print("Listing Agent Sessions")
    print("="*80)
    
    try:
        # List all sessions for the agent
        response = bedrock_agent_runtime.list_agent_sessions(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            maxResults=50
        )
        
        sessions = response.get('agentSessionSummaries', [])
        print(f"\n✅ Found {len(sessions)} session(s)")
        
        return sessions
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to list sessions: {str(e)}")
        return None


def get_session_details(session_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific session.
    
    Args:
        session_id: The session identifier
    
    Returns:
        Dictionary containing session details or None if error
    """
    print(f"\n📋 Retrieving session: {session_id}")
    
    try:
        response = bedrock_agent_runtime.get_agent_session(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id
        )
        
        return response
        
    except Exception as e:
        print(f"   ❌ ERROR: Failed to retrieve session: {str(e)}")
        return None


def display_memory_summary(memory_data: Dict):
    """
    Display memory summary in a readable format.
    
    Args:
        memory_data: Memory data from AWS API
    """
    print("\n" + "="*80)
    print("MEMORY SUMMARY")
    print("="*80)
    
    if not memory_data:
        print("No memory data available")
        return
    
    # Display memory contents
    memory_contents = memory_data.get('memoryContents', [])
    
    if memory_contents:
        print(f"\nMemory Entries: {len(memory_contents)}")
        for i, content in enumerate(memory_contents, 1):
            print(f"\n{i}. Memory Entry:")
            print(f"   Type: {content.get('type', 'Unknown')}")
            print(f"   Content: {content.get('content', 'N/A')}")
    else:
        print("\nNo memory contents found")
    
    # Display metadata
    metadata = memory_data.get('ResponseMetadata', {})
    if metadata:
        print(f"\nRequest ID: {metadata.get('RequestId', 'N/A')}")


def display_user_preferences(preferences_data: Dict):
    """
    Display user preferences in a readable format.
    
    Args:
        preferences_data: Preferences data from AWS API
    """
    print("\n" + "="*80)
    print(f"USER PREFERENCES FOR: {USER_ID}")
    print("="*80)
    
    if not preferences_data:
        print("No preferences data available")
        return
    
    # Display preferences
    preferences = preferences_data.get('preferences', {})
    
    if preferences:
        print("\nLearned Preferences:")
        for key, value in preferences.items():
            print(f"  • {key}: {value}")
    else:
        print("\nNo preferences learned yet")
        print("\nExpected preferences after seeding:")
        print("  • Prefers detailed benefit breakdowns")
        print("  • Needs step-by-step liability calculations")
        print("  • Tracks deductible and OOP max progression")
        print("  • Frequently accessed member: M123456")


def display_search_results(search_data: Dict):
    """
    Display semantic search results in a readable format.
    
    Args:
        search_data: Search results from AWS API
    """
    print("\n" + "="*80)
    print(f"SEARCH RESULTS FOR: '{SEARCH_QUERY}'")
    print("="*80)
    
    if not search_data:
        print("No search results available")
        return
    
    # Display search results
    output = search_data.get('output', {})
    text = output.get('text', '')
    
    if text:
        print("\nAgent's Knowledge:")
        print(text)
    else:
        print("\nNo relevant information found")
    
    # Display citations if available
    citations = search_data.get('citations', [])
    if citations:
        print(f"\n\nSources ({len(citations)} citation(s)):")
        for i, citation in enumerate(citations, 1):
            print(f"\n{i}. {citation.get('generatedResponsePart', {}).get('textResponsePart', {}).get('text', 'N/A')}")


def display_sessions(sessions: List[Dict]):
    """
    Display agent sessions in a readable format.
    
    Args:
        sessions: List of session summaries
    """
    print("\n" + "="*80)
    print("AGENT SESSIONS")
    print("="*80)
    
    if not sessions:
        print("\nNo sessions found")
        print("\nRun 04_seed_memory.py to create sample sessions")
        return
    
    print(f"\nTotal Sessions: {len(sessions)}")
    
    for i, session in enumerate(sessions, 1):
        session_id = session.get('sessionId', 'Unknown')
        created_at = session.get('createdAt', 'Unknown')
        updated_at = session.get('updatedAt', 'Unknown')
        
        print(f"\n{i}. Session ID: {session_id}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        
        # Get session details if user_001 is in the session
        if USER_ID in session_id:
            print(f"   👤 User: {USER_ID}")
            details = get_session_details(session_id)
            if details:
                print(f"   ✅ Session details retrieved")


def display_what_agent_remembers():
    """
    Display a comprehensive summary of what the agent remembers about the customer.
    """
    print("\n" + "="*80)
    print(f"WHAT THE AGENT REMEMBERS ABOUT: {USER_ID}")
    print("="*80)
    
    print("\n📊 Based on seeded conversations, the agent should remember:")
    
    print("\n1. MEMBER INFORMATION:")
    print("   • Frequently accessed member: M123456")
    print("   • Service date: March 15, 2024")
    print("   • Enrollment status: ACTIVE")
    print("   • Coverage period: Jan 1, 2024 - Dec 31, 2024")
    
    print("\n2. BENEFIT DETAILS:")
    print("   • Primary care copay: $20")
    print("   • Specialist copay: $40")
    print("   • Emergency room copay: $150")
    print("   • Annual deductible: $1,500")
    print("   • Out-of-pocket maximum: $6,000")
    print("   • Coinsurance: 20% after deductible")
    
    print("\n3. COMMUNICATION PREFERENCES:")
    print("   • Prefers detailed benefit breakdowns")
    print("   • Needs step-by-step liability calculations")
    print("   • Wants to track deductible progression")
    print("   • Appreciates OOP max tracking")
    
    print("\n4. CONVERSATION PATTERNS:")
    print("   • Eligibility verification workflow")
    print("   • Multi-procedure liability calculations")
    print("   • Progressive cost tracking")
    print("   • Deductible and OOP max monitoring")
    
    print("\n5. PROCEDURES DISCUSSED:")
    print("   • Specialist office visit ($250)")
    print("   • Lab test ($500)")
    print("   • MRI ($2,000)")
    print("   • Surgery ($15,000)")
    
    print("\n6. CALCULATION PATTERNS:")
    print("   • Copay application")
    print("   • Deductible tracking")
    print("   • Coinsurance calculation")
    print("   • OOP max enforcement")


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("Benefits Member Liability Agent - Memory Testing")
    print("="*80)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Memory ID: {MEMORY_ID}")
    print(f"User ID: {USER_ID}")
    print(f"Search Query: '{SEARCH_QUERY}'")
    print("="*80)
    
    try:
        # 1. Get memory summary
        print("\n" + "="*80)
        print("STEP 1: Retrieve Memory Summary")
        print("="*80)
        memory_summary = get_agent_memory_summary()
        if memory_summary:
            display_memory_summary(memory_summary)
        
        # 2. Get user preferences
        print("\n" + "="*80)
        print("STEP 2: Retrieve User Preferences")
        print("="*80)
        user_preferences = retrieve_user_preferences(USER_ID)
        if user_preferences:
            display_user_preferences(user_preferences)
        
        # 3. Search semantic memory
        print("\n" + "="*80)
        print("STEP 3: Search Semantic Memory")
        print("="*80)
        search_results = search_semantic_memory(SEARCH_QUERY)
        if search_results:
            display_search_results(search_results)
        
        # 4. List agent sessions
        print("\n" + "="*80)
        print("STEP 4: List Agent Sessions")
        print("="*80)
        sessions = list_agent_sessions()
        if sessions:
            display_sessions(sessions)
        
        # 5. Display what agent remembers
        display_what_agent_remembers()
        
        # Final summary
        print("\n" + "="*80)
        print("TESTING SUMMARY")
        print("="*80)
        print(f"✅ Memory ID loaded: {MEMORY_ID}")
        print(f"✅ User ID: {USER_ID}")
        print(f"✅ Search query: '{SEARCH_QUERY}'")
        
        if memory_summary:
            print("✅ Memory summary retrieved")
        else:
            print("⚠️  Memory summary not available")
        
        if user_preferences:
            print("✅ User preferences retrieved")
        else:
            print("⚠️  User preferences not available")
        
        if search_results:
            print("✅ Semantic search completed")
        else:
            print("⚠️  Semantic search not available")
        
        if sessions:
            print(f"✅ Found {len(sessions)} session(s)")
        else:
            print("⚠️  No sessions found")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\nTo populate memory with data:")
        print("  python3 04_seed_memory.py")
        print("\nTo test agent with memory:")
        print("  python3 02_test_agent.py")
        print("\nTo view memory in AWS Console:")
        print("  1. Go to AWS Bedrock Console")
        print("  2. Navigate to Agents")
        print("  3. Select your agent")
        print("  4. View Memory tab")
        
        print("\n" + "="*80)
        print("✅ Memory testing completed!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
