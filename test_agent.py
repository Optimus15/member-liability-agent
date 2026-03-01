#!/usr/bin/env python3
"""
Test script for Benefits Member Liability Agent
This script tests the Bedrock Agent with sample queries.

NOTE: Update agent_id and alias_id with your actual values from agent_config.json
"""

import boto3
import json
import sys
from typing import Iterator

# Load agent configuration
try:
    with open('agent_config.json', 'r') as f:
        config = json.load(f)
        AGENT_ID = config['agent_id']
        ALIAS_ID = config['alias_id']
except FileNotFoundError:
    print("ERROR: agent_config.json not found. Run create_agent.py first.")
    sys.exit(1)

# Initialize Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')


def invoke_agent(query: str, session_id: str = 'test-session') -> str:
    """
    Invoke the Bedrock Agent with a query.
    
    Args:
        query: The user's question or request
        session_id: Session identifier for conversation continuity
    
    Returns:
        The agent's response as a string
    """
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id,
            inputText=query
        )
        
        # Process streaming response
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                chunk_text = chunk['bytes'].decode('utf-8')
                full_response += chunk_text
                print(chunk_text, end='', flush=True)
        
        print("\n")
        return full_response
        
    except Exception as e:
        print(f"ERROR: Failed to invoke agent: {str(e)}")
        return ""


def test_eligibility_check():
    """Test eligibility check functionality."""
    print("\n" + "="*80)
    print("TEST 1: Eligibility Check")
    print("="*80)
    
    queries = [
        "Check eligibility for member M123456 on 2024-03-15",
        "Is member M789012 eligible for benefits on 2024-06-20?",
        "What is the enrollment status for member M345678?"
    ]
    
    for query in queries:
        response = invoke_agent(query, session_id='test-eligibility')
        # Add a small delay between requests
        import time
        time.sleep(2)


def test_liability_calculation():
    """Test liability calculation functionality."""
    print("\n" + "="*80)
    print("TEST 2: Liability Calculation")
    print("="*80)
    
    queries = [
        "Calculate liability for member M123456 claim C789",
        "What is the member liability for claim C456 for member M789012?",
        "How much will member M123456 pay for a $150 primary care visit?"
    ]
    
    for query in queries:
        response = invoke_agent(query, session_id='test-liability')
        import time
        time.sleep(2)


def test_knowledge_base_retrieval():
    """Test Knowledge Base retrieval functionality."""
    print("\n" + "="*80)
    print("TEST 3: Knowledge Base Retrieval")
    print("="*80)
    
    queries = [
        "What are the policy rules for PPO plans?",
        "Explain the deductible and out-of-pocket maximum",
        "What services require prior authorization?",
        "What is the copay for primary care visits?"
    ]
    
    for query in queries:
        response = invoke_agent(query, session_id='test-kb')
        import time
        time.sleep(2)


def test_combined_workflow():
    """Test combined eligibility check and liability calculation."""
    print("\n" + "="*80)
    print("TEST 4: Combined Workflow")
    print("="*80)
    
    session_id = 'test-combined'
    
    # Step 1: Check eligibility
    invoke_agent(
        "Check if member M123456 is eligible for benefits on 2024-03-15",
        session_id=session_id
    )
    
    import time
    time.sleep(2)
    
    # Step 2: Calculate liability (in same session)
    invoke_agent(
        "Now calculate the liability for this member for a $150 office visit",
        session_id=session_id
    )


def interactive_mode():
    """Interactive mode for testing custom queries."""
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("Enter your queries (type 'exit' to quit)")
    print()
    
    session_id = 'interactive-session'
    
    while True:
        try:
            query = input("\nYou: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Exiting interactive mode...")
                break
            
            if not query:
                continue
            
            invoke_agent(query, session_id=session_id)
            
        except KeyboardInterrupt:
            print("\n\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"ERROR: {str(e)}")


def main():
    """Main test execution."""
    print("="*80)
    print("Benefits Member Liability Agent - Test Suite")
    print("="*80)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Alias ID: {ALIAS_ID}")
    print("="*80)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'eligibility':
            test_eligibility_check()
        elif test_type == 'liability':
            test_liability_calculation()
        elif test_type == 'kb':
            test_knowledge_base_retrieval()
        elif test_type == 'combined':
            test_combined_workflow()
        elif test_type == 'interactive':
            interactive_mode()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available tests: eligibility, liability, kb, combined, interactive")
    else:
        # Run all tests
        print("\nRunning all tests...\n")
        test_eligibility_check()
        test_liability_calculation()
        test_knowledge_base_retrieval()
        test_combined_workflow()
        
        # Offer interactive mode
        print("\n" + "="*80)
        response = input("Would you like to enter interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            interactive_mode()
    
    print("\n" + "="*80)
    print("Test suite completed!")
    print("="*80)


if __name__ == '__main__':
    main()
