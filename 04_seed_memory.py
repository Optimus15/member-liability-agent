#!/usr/bin/env python3
"""
Seed Memory for Benefits Member Liability Agent
This script adds sample member and provider conversations to the agent's memory
to help the memory system learn preferences and context.

Customer ID: user_001

Conversations:
1. Member eligibility and benefits inquiry
2. Member liability calculation for various services

Usage:
    python3 04_seed_memory.py
"""

import boto3
import json
import sys
import time
from datetime import datetime
from typing import Dict, List

# Configuration
CUSTOMER_ID = 'user_001'
MEMORY_PROCESSING_WAIT = 30  # seconds

# Load agent and memory configuration
try:
    with open('agent_config.json', 'r') as f:
        agent_config = json.load(f)
        AGENT_ID = agent_config['agent_id']
        ALIAS_ID = agent_config['alias_id']
except FileNotFoundError:
    print("ERROR: agent_config.json not found. Run create_agent.py first.")
    sys.exit(1)

try:
    with open('memory_config.json', 'r') as f:
        memory_config = json.load(f)
        MEMORY_ID = memory_config['memory_id']
except FileNotFoundError:
    print("ERROR: memory_config.json not found. Run 03_create_memory.py first.")
    sys.exit(1)

# Initialize Bedrock Agent Runtime client
# NOTE: This client is used to invoke the agent and store conversation history
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')


def create_conversation_1() -> List[Dict]:
    """
    Conversation 1: Member eligibility and benefits inquiry
    
    Scenario: A provider is checking if a member is eligible for benefits
    and what benefits are available.
    
    Returns:
        List of conversation turns (user and agent messages)
    """
    return [
        {
            'role': 'user',
            'content': 'Hi, I need to check eligibility for member M123456. Can you help?'
        },
        {
            'role': 'assistant',
            'content': 'Of course! I can help you check member eligibility. To verify eligibility, I need the member ID and the date of service. You mentioned member M123456. What is the date of service?'
        },
        {
            'role': 'user',
            'content': 'The service date is March 15, 2024.'
        },
        {
            'role': 'assistant',
            'content': 'Let me check the eligibility for member M123456 on March 15, 2024. Based on the eligibility check, member M123456 is ACTIVE and eligible for benefits. The coverage period is from January 1, 2024 to December 31, 2024. The member has comprehensive health benefits including medical, dental, and vision coverage.'
        },
        {
            'role': 'user',
            'content': 'Great! What specific benefits does this member have?'
        },
        {
            'role': 'assistant',
            'content': 'Member M123456 has the following benefits:\n\n1. Medical Benefits:\n   - Primary care visits: $20 copay\n   - Specialist visits: $40 copay\n   - Emergency room: $150 copay\n   - Annual deductible: $1,500 (individual)\n   - Out-of-pocket maximum: $6,000\n   - Coinsurance: 20% after deductible\n\n2. Prescription Benefits:\n   - Generic drugs: $10 copay\n   - Brand name drugs: $30 copay\n   - Specialty drugs: $50 copay\n\n3. Preventive Care:\n   - Annual physical exam: Covered 100%\n   - Immunizations: Covered 100%\n   - Screenings: Covered 100%\n\nThe member is in good standing with no restrictions on benefits.'
        },
        {
            'role': 'user',
            'content': 'Perfect, thank you for the detailed information!'
        },
        {
            'role': 'assistant',
            'content': 'You\'re welcome! If you need to calculate member liability for any specific services or have other questions about this member\'s benefits, feel free to ask.'
        }
    ]


def create_conversation_2() -> List[Dict]:
    """
    Conversation 2: Member liability calculation for various services
    
    Scenario: A provider is asking about member liability for different
    medical procedures and services.
    
    Returns:
        List of conversation turns (user and agent messages)
    """
    return [
        {
            'role': 'user',
            'content': 'I need to calculate member liability for member M123456 for several procedures. Can you help?'
        },
        {
            'role': 'assistant',
            'content': 'Absolutely! I can help calculate member liability for various procedures. Please provide the details of the procedures, including the service codes and charges.'
        },
        {
            'role': 'user',
            'content': 'First, we have an office visit with a specialist. The total charge is $250.'
        },
        {
            'role': 'assistant',
            'content': 'For a specialist office visit with a total charge of $250:\n\nMember Liability Breakdown:\n- Copay: $40 (specialist visit copay)\n- Deductible applied: $210 (remaining charge after copay)\n- Coinsurance: $0 (deductible not yet met)\n- Total Member Liability: $250\n\nRemaining deductible: $1,290 (started at $1,500)\nRemaining out-of-pocket maximum: $5,750\n\nNote: Since the member hasn\'t met their annual deductible yet, they are responsible for the full amount after the copay.'
        },
        {
            'role': 'user',
            'content': 'What about a lab test that costs $500?'
        },
        {
            'role': 'assistant',
            'content': 'For a lab test with a total charge of $500:\n\nMember Liability Breakdown:\n- Copay: $0 (lab tests typically don\'t have copays)\n- Deductible applied: $500 (applied to remaining deductible)\n- Coinsurance: $0 (deductible still not met)\n- Total Member Liability: $500\n\nRemaining deductible: $790 (was $1,290, now $790)\nRemaining out-of-pocket maximum: $5,250\n\nThe member is getting closer to meeting their deductible. Once the deductible is met, they will only pay 20% coinsurance on covered services.'
        },
        {
            'role': 'user',
            'content': 'And if they need an MRI that costs $2,000?'
        },
        {
            'role': 'assistant',
            'content': 'For an MRI with a total charge of $2,000:\n\nMember Liability Breakdown:\n- Copay: $0 (imaging typically doesn\'t have copays)\n- Deductible applied: $790 (remaining deductible)\n- Coinsurance: $242 (20% of $1,210 after deductible is met)\n- Total Member Liability: $1,032\n\nRemaining deductible: $0 (deductible is now met!)\nRemaining out-of-pocket maximum: $4,218\n\nGood news! After this MRI, the member will have met their annual deductible. For the rest of the year, they will only pay 20% coinsurance on covered services until they reach their out-of-pocket maximum of $6,000.'
        },
        {
            'role': 'user',
            'content': 'That\'s very helpful. What if they need surgery that costs $15,000?'
        },
        {
            'role': 'assistant',
            'content': 'For surgery with a total charge of $15,000:\n\nMember Liability Breakdown:\n- Copay: $0 (surgery doesn\'t have copays)\n- Deductible applied: $0 (deductible already met)\n- Coinsurance: $3,000 (20% of $15,000)\n- Out-of-pocket maximum applied: $4,218 (member hits OOP max)\n- Total Member Liability: $4,218\n\nRemaining deductible: $0 (already met)\nRemaining out-of-pocket maximum: $0 (OOP max reached!)\n\nExcellent news! After this surgery, the member will have reached their out-of-pocket maximum for the year. This means all covered services for the rest of the year will be paid 100% by insurance with no additional cost to the member.'
        },
        {
            'role': 'user',
            'content': 'Excellent! This is exactly what I needed. Thank you!'
        },
        {
            'role': 'assistant',
            'content': 'You\'re very welcome! I\'ve calculated the member liability for multiple procedures and tracked the deductible and out-of-pocket maximum progression. If you need any other calculations or have questions about member benefits, I\'m here to help!'
        }
    ]


def store_conversation_in_memory(
    session_id: str,
    conversation: List[Dict],
    conversation_title: str
) -> bool:
    """
    Store a conversation in the agent's memory by invoking the agent
    with the conversation turns.
    
    NOTE: AWS Bedrock Agent Memory automatically captures conversations
    when you invoke the agent. We simulate a conversation by sending
    the messages through the agent.
    
    Args:
        session_id: Unique session identifier
        conversation: List of conversation turns
        conversation_title: Title/description of the conversation
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"Storing Conversation: {conversation_title}")
    print(f"Session ID: {session_id}")
    print(f"{'='*80}\n")
    
    try:
        # Store each user message by invoking the agent
        # The agent's responses are automatically captured in memory
        for i, turn in enumerate(conversation):
            if turn['role'] == 'user':
                print(f"Turn {i+1} - User: {turn['content'][:80]}...")
                
                # Invoke agent with user message
                # NOTE: The agent will process this and store it in memory
                response = bedrock_agent_runtime.invoke_agent(
                    agentId=AGENT_ID,
                    agentAliasId=ALIAS_ID,
                    sessionId=session_id,
                    inputText=turn['content'],
                    enableTrace=False,
                    sessionState={
                        'sessionAttributes': {
                            'customerId': CUSTOMER_ID,
                            'conversationTitle': conversation_title
                        }
                    }
                )
                
                # Process the streaming response
                for event in response['completion']:
                    if 'chunk' in event:
                        # Agent response is automatically stored in memory
                        pass
                
                print(f"  ✓ Stored in memory")
                
                # Small delay between turns to simulate natural conversation
                time.sleep(1)
        
        print(f"\n✅ Conversation stored successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to store conversation: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify agent exists and is in PREPARED state")
        print("2. Check that memory is associated with the agent")
        print("3. Ensure AWS credentials are configured")
        print("4. Review CloudWatch logs for detailed errors")
        return False


def seed_memory():
    """
    Main function to seed the agent memory with sample conversations.
    """
    print("\n" + "="*80)
    print("Benefits Member Liability Agent - Memory Seeding")
    print("="*80)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Alias ID: {ALIAS_ID}")
    print(f"Memory ID: {MEMORY_ID}")
    print(f"Customer ID: {CUSTOMER_ID}")
    print("="*80)
    
    # Generate unique session IDs for each conversation
    timestamp = int(time.time())
    session_1 = f"{CUSTOMER_ID}_eligibility_{timestamp}"
    session_2 = f"{CUSTOMER_ID}_liability_{timestamp + 1}"
    
    # Conversation 1: Eligibility and Benefits
    print("\n" + "="*80)
    print("CONVERSATION 1: Member Eligibility and Benefits Inquiry")
    print("="*80)
    
    conversation_1 = create_conversation_1()
    success_1 = store_conversation_in_memory(
        session_id=session_1,
        conversation=conversation_1,
        conversation_title="Member Eligibility and Benefits Inquiry"
    )
    
    if not success_1:
        print("\n⚠️  WARNING: Failed to store conversation 1")
        print("Continuing with conversation 2...")
    
    # Small delay between conversations
    time.sleep(2)
    
    # Conversation 2: Liability Calculations
    print("\n" + "="*80)
    print("CONVERSATION 2: Member Liability Calculations")
    print("="*80)
    
    conversation_2 = create_conversation_2()
    success_2 = store_conversation_in_memory(
        session_id=session_2,
        conversation=conversation_2,
        conversation_title="Member Liability Calculations for Multiple Procedures"
    )
    
    if not success_2:
        print("\n⚠️  WARNING: Failed to store conversation 2")
    
    # Wait for memory system to process and extract preferences
    print("\n" + "="*80)
    print("MEMORY PROCESSING")
    print("="*80)
    print(f"\n⏳ Waiting {MEMORY_PROCESSING_WAIT} seconds for memory system to process...")
    print("   The memory system will:")
    print("   - Extract conversation summaries")
    print("   - Identify user preferences")
    print("   - Build semantic memory index")
    print("   - Store member interaction patterns")
    
    for i in range(MEMORY_PROCESSING_WAIT):
        time.sleep(1)
        if (i + 1) % 10 == 0:
            print(f"   {i + 1}/{MEMORY_PROCESSING_WAIT} seconds elapsed...")
    
    print(f"\n✅ Memory processing wait complete!")
    
    # Summary
    print("\n" + "="*80)
    print("SEEDING SUMMARY")
    print("="*80)
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Conversations stored: {sum([success_1, success_2])}/2")
    print(f"\nConversation 1 (Eligibility): {'✅ SUCCESS' if success_1 else '❌ FAILED'}")
    print(f"Conversation 2 (Liability): {'✅ SUCCESS' if success_2 else '❌ FAILED'}")
    
    print("\n" + "="*80)
    print("EXPECTED MEMORY LEARNING")
    print("="*80)
    print("\nThe agent's memory should now contain:")
    print("\n1. SESSION SUMMARIES:")
    print("   - Member eligibility verification workflow")
    print("   - Liability calculation for multiple procedures")
    print("   - Deductible and OOP max tracking patterns")
    
    print("\n2. USER PREFERENCES:")
    print("   - Customer prefers detailed benefit breakdowns")
    print("   - Customer needs step-by-step liability calculations")
    print("   - Customer tracks deductible and OOP max progression")
    print("   - Frequently accessed member: M123456")
    
    print("\n3. SEMANTIC MEMORY:")
    print("   - Eligibility verification patterns")
    print("   - Liability calculation methodologies")
    print("   - Benefit explanation approaches")
    print("   - Multi-procedure cost tracking")
    
    print("\n" + "="*80)
    print("VERIFICATION STEPS")
    print("="*80)
    print("\nTo verify memory was stored correctly:")
    print("\n1. Test agent with similar queries:")
    print("   python3 02_test_agent.py")
    print("\n2. Check if agent remembers member M123456")
    print("\n3. Verify agent provides detailed breakdowns (learned preference)")
    print("\n4. View memory contents:")
    print(f"   aws bedrock-agent get-agent-memory \\")
    print(f"     --agent-id {AGENT_ID} \\")
    print(f"     --memory-id {MEMORY_ID}")
    print("\n5. List all sessions:")
    print(f"   aws bedrock-agent-runtime list-agent-sessions \\")
    print(f"     --agent-id {AGENT_ID} \\")
    print(f"     --agent-alias-id {ALIAS_ID}")
    
    if success_1 and success_2:
        print("\n" + "="*80)
        print("✅ SUCCESS: Memory seeding completed!")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("⚠️  PARTIAL SUCCESS: Some conversations failed to store")
        print("="*80)
        return 1


def main():
    """Main execution."""
    try:
        exit_code = seed_memory()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Seeding failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
