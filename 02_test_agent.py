#!/usr/bin/env python3
"""
Test script for Benefits Member Liability Agent - Workflow Test
This script tests the agent with a specific workflow:
1. Check if member is eligible
2. Verify member has benefits
3. Calculate member liability once eligibility and benefits are validated
4. Use retrieve tool to search knowledge base if available

Usage:
    python3 02_test_agent.py [member_id] [service_date]
    
Example:
    python3 02_test_agent.py M123456 2024-03-15
"""

import boto3
import json
import sys
import time
from typing import Dict, Optional, Tuple

# Configuration
DEFAULT_MEMBER_ID = 'M123456'
DEFAULT_SERVICE_DATE = '2024-03-15'
DEFAULT_CLAIM_AMOUNT = 150.00

# Load agent configuration
try:
    with open('agent_config.json', 'r') as f:
        config = json.load(f)
        AGENT_ID = config['agent_id']
        ALIAS_ID = config['alias_id']
        KB_ID = config.get('knowledge_base_id', '<PLACE-YOUR-KB-ID>')
except FileNotFoundError:
    print("ERROR: agent_config.json not found. Run create_agent.py first.")
    sys.exit(1)

# Initialize Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')


class AgentResponse:
    """Container for agent response data."""
    def __init__(self, text: str, success: bool = True, error: Optional[str] = None):
        self.text = text
        self.success = success
        self.error = error
        
    def __str__(self):
        return self.text


def invoke_agent(query: str, session_id: str, enable_trace: bool = False) -> AgentResponse:
    """
    Invoke the Bedrock Agent with a query.
    
    Args:
        query: The user's question or request
        session_id: Session identifier for conversation continuity
        enable_trace: Whether to enable trace output for debugging
    
    Returns:
        AgentResponse object containing the response text and metadata
    """
    print(f"\n{'='*80}")
    print(f"🤖 Query: {query}")
    print(f"{'='*80}\n")
    
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id,
            inputText=query,
            enableTrace=enable_trace
        )
        
        # Process streaming response
        full_response = ""
        trace_data = []
        
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                chunk_text = chunk['bytes'].decode('utf-8')
                full_response += chunk_text
                print(chunk_text, end='', flush=True)
            
            # Capture trace information if enabled
            if enable_trace and 'trace' in event:
                trace_data.append(event['trace'])
        
        print("\n")
        
        # Display trace information if enabled
        if enable_trace and trace_data:
            print("\n📊 Trace Information:")
            for trace in trace_data:
                if 'trace' in trace:
                    trace_info = trace['trace']
                    if 'orchestrationTrace' in trace_info:
                        orch = trace_info['orchestrationTrace']
                        if 'invocationInput' in orch:
                            print(f"  - Action: {orch['invocationInput'].get('actionGroupInvocationInput', {}).get('actionGroupName', 'N/A')}")
                        if 'observation' in orch:
                            print(f"  - Observation: {orch['observation'].get('type', 'N/A')}")
        
        return AgentResponse(text=full_response, success=True)
        
    except Exception as e:
        error_msg = f"Failed to invoke agent: {str(e)}"
        print(f"❌ ERROR: {error_msg}\n")
        return AgentResponse(text="", success=False, error=error_msg)


def check_eligibility(member_id: str, service_date: str, session_id: str) -> Tuple[bool, AgentResponse]:
    """
    Step 1: Check if member is eligible for benefits.
    
    Args:
        member_id: Member identifier
        service_date: Date of service (YYYY-MM-DD)
        session_id: Session identifier
    
    Returns:
        Tuple of (is_eligible, response)
    """
    print("\n" + "="*80)
    print("STEP 1: Checking Member Eligibility")
    print("="*80)
    
    query = f"Is member {member_id} eligible for benefits on {service_date}?"
    response = invoke_agent(query, session_id, enable_trace=True)
    
    if not response.success:
        return False, response
    
    # Simple heuristic to determine eligibility from response
    # In production, you'd parse structured response
    response_lower = response.text.lower()
    is_eligible = (
        'eligible' in response_lower and 
        'not eligible' not in response_lower and
        'ineligible' not in response_lower
    )
    
    if is_eligible:
        print("\n✅ Result: Member appears to be ELIGIBLE")
    else:
        print("\n❌ Result: Member appears to be INELIGIBLE or status unclear")
    
    return is_eligible, response


def check_benefits(member_id: str, session_id: str) -> Tuple[bool, AgentResponse]:
    """
    Step 2: Check if member has benefits.
    
    Args:
        member_id: Member identifier
        session_id: Session identifier
    
    Returns:
        Tuple of (has_benefits, response)
    """
    print("\n" + "="*80)
    print("STEP 2: Checking Member Benefits")
    print("="*80)
    
    query = f"Does member {member_id} have benefits? What benefits are available?"
    response = invoke_agent(query, session_id, enable_trace=True)
    
    if not response.success:
        return False, response
    
    # Simple heuristic to determine if benefits exist
    response_lower = response.text.lower()
    has_benefits = (
        'benefit' in response_lower and
        ('no benefit' not in response_lower or 'has benefit' in response_lower)
    )
    
    if has_benefits:
        print("\n✅ Result: Member appears to HAVE benefits")
    else:
        print("\n❌ Result: Member benefits unclear or not found")
    
    return has_benefits, response


def calculate_liability(member_id: str, claim_amount: float, session_id: str) -> AgentResponse:
    """
    Step 3: Calculate member liability once eligibility and benefits are validated.
    
    Args:
        member_id: Member identifier
        claim_amount: Claim amount in dollars
        session_id: Session identifier
    
    Returns:
        AgentResponse with liability calculation
    """
    print("\n" + "="*80)
    print("STEP 3: Calculating Member Liability")
    print("="*80)
    
    query = (
        f"Calculate the member liability for member {member_id} "
        f"for a ${claim_amount:.2f} claim. "
        f"Provide a detailed breakdown including deductible, copay, coinsurance, "
        f"and out-of-pocket maximum."
    )
    response = invoke_agent(query, session_id, enable_trace=True)
    
    if response.success:
        print("\n✅ Result: Liability calculation completed")
    else:
        print("\n❌ Result: Liability calculation failed")
    
    return response


def search_knowledge_base(session_id: str) -> AgentResponse:
    """
    Step 4: Use retrieve tool to search the knowledge base if available.
    
    Args:
        session_id: Session identifier
    
    Returns:
        AgentResponse with knowledge base information
    """
    print("\n" + "="*80)
    print("STEP 4: Searching Knowledge Base")
    print("="*80)
    
    if KB_ID == '<PLACE-YOUR-KB-ID>':
        print("⚠️  WARNING: Knowledge Base ID is placeholder. Skipping KB search.")
        print("   Update kb_config.json with actual Knowledge Base ID to enable this feature.")
        return AgentResponse(
            text="Knowledge Base not configured",
            success=False,
            error="KB ID is placeholder"
        )
    
    query = (
        "Search the knowledge base for information about policy rules, "
        "deductibles, copays, and out-of-pocket maximums. "
        "What are the standard benefit rules?"
    )
    response = invoke_agent(query, session_id, enable_trace=True)
    
    if response.success:
        print("\n✅ Result: Knowledge base search completed")
    else:
        print("\n❌ Result: Knowledge base search failed")
    
    return response


def run_workflow(member_id: str, service_date: str, claim_amount: float):
    """
    Run the complete workflow test.
    
    Args:
        member_id: Member identifier
        service_date: Date of service (YYYY-MM-DD)
        claim_amount: Claim amount in dollars
    """
    print("\n" + "="*80)
    print("Benefits Member Liability Agent - Workflow Test")
    print("="*80)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Alias ID: {ALIAS_ID}")
    print(f"Knowledge Base ID: {KB_ID}")
    print(f"\nTest Parameters:")
    print(f"  Member ID: {member_id}")
    print(f"  Service Date: {service_date}")
    print(f"  Claim Amount: ${claim_amount:.2f}")
    print("="*80)
    
    # Use a single session for conversation continuity
    session_id = f'workflow-test-{int(time.time())}'
    
    # Step 1: Check eligibility
    is_eligible, eligibility_response = check_eligibility(member_id, service_date, session_id)
    time.sleep(2)  # Delay between requests
    
    if not is_eligible:
        print("\n" + "="*80)
        print("⚠️  WORKFLOW STOPPED: Member is not eligible")
        print("="*80)
        print("\nCannot proceed with benefits check and liability calculation.")
        return
    
    # Step 2: Check benefits
    has_benefits, benefits_response = check_benefits(member_id, session_id)
    time.sleep(2)  # Delay between requests
    
    if not has_benefits:
        print("\n" + "="*80)
        print("⚠️  WORKFLOW WARNING: Member benefits unclear")
        print("="*80)
        print("\nProceeding with liability calculation anyway...")
    
    # Step 3: Calculate liability (only if eligible)
    liability_response = calculate_liability(member_id, claim_amount, session_id)
    time.sleep(2)  # Delay between requests
    
    # Step 4: Search knowledge base
    kb_response = search_knowledge_base(session_id)
    
    # Final summary
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    print(f"✅ Eligibility Check: {'PASSED' if is_eligible else 'FAILED'}")
    print(f"{'✅' if has_benefits else '⚠️ '} Benefits Check: {'PASSED' if has_benefits else 'UNCLEAR'}")
    print(f"{'✅' if liability_response.success else '❌'} Liability Calculation: {'COMPLETED' if liability_response.success else 'FAILED'}")
    print(f"{'✅' if kb_response.success else '⚠️ '} Knowledge Base Search: {'COMPLETED' if kb_response.success else 'SKIPPED/FAILED'}")
    print("="*80)
    
    # Save results to file
    results = {
        'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'session_id': session_id,
        'parameters': {
            'member_id': member_id,
            'service_date': service_date,
            'claim_amount': claim_amount
        },
        'results': {
            'eligibility': {
                'is_eligible': is_eligible,
                'response': eligibility_response.text,
                'success': eligibility_response.success
            },
            'benefits': {
                'has_benefits': has_benefits,
                'response': benefits_response.text,
                'success': benefits_response.success
            },
            'liability': {
                'response': liability_response.text,
                'success': liability_response.success
            },
            'knowledge_base': {
                'response': kb_response.text,
                'success': kb_response.success
            }
        }
    }
    
    results_file = f'test_results_{session_id}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to: {results_file}")


def main():
    """Main execution."""
    # Parse command line arguments
    member_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MEMBER_ID
    service_date = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SERVICE_DATE
    claim_amount = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_CLAIM_AMOUNT
    
    try:
        run_workflow(member_id, service_date, claim_amount)
        print("\n✅ Workflow test completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
