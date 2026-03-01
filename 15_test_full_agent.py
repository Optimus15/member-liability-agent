#!/usr/bin/env python3
"""
Test Script for Full-Featured Member Liability Agent
This script tests the agent with memory and gateway integration.

Test Scenario:
- User: user_001
- Query: "Hi! Can you look up my eligibility and benefits"
- Verifies:
  1. Agent remembers customer prefers email (from memory)
  2. Agent combines memory with eligibility lookup
  3. Agent provides personalized response

Usage:
    python3 15_test_full_agent.py
"""

import boto3
import json
import sys
import time
import os
from typing import Dict, Optional, List
from datetime import datetime

# Configuration Files
FULL_AGENT_CONFIG_FILE = 'full_agent_config.json'
MEMORY_CONFIG_FILE = 'memory_config.json'
GATEWAY_CONFIG_FILE = 'gateway_config.json'
KB_CONFIG_FILE = 'kb_config.json'

# Test Configuration
TEST_USER_ID = 'user_001'
TEST_QUERY = "Hi! Can you look up my eligibility and benefits"
TEST_MEMBER_ID = 'M123456'
TEST_SERVICE_DATE = '2024-03-15'

# Initialize AWS clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')


class TestResult:
    """Container for test result data."""
    def __init__(self, name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class AgentTester:
    """Test harness for full-featured agent."""
    
    def __init__(self):
        self.agent_id = None
        self.alias_id = None
        self.memory_id = None
        self.gateway_api_id = None
        self.kb_id = None
        self.test_results = []
        
    def load_configurations(self) -> bool:
        """Load all configuration files."""
        print("\n" + "="*80)
        print("Loading Configuration Files")
        print("="*80)
        
        try:
            # Load agent configuration
            with open(FULL_AGENT_CONFIG_FILE, 'r') as f:
                agent_config = json.load(f)
                self.agent_id = agent_config['agent_id']
                self.alias_id = agent_config['alias_id']
                self.memory_id = agent_config.get('memory_id')
                self.gateway_api_id = agent_config.get('gateway_api_id')
                self.kb_id = agent_config.get('knowledge_base_id')
            
            print(f"✅ Loaded agent configuration")
            print(f"   Agent ID: {self.agent_id}")
            print(f"   Alias ID: {self.alias_id}")
            print(f"   Memory ID: {self.memory_id or 'Not configured'}")
            print(f"   Gateway API ID: {self.gateway_api_id or 'Not configured'}")
            print(f"   Knowledge Base ID: {self.kb_id or 'Not configured'}")
            
            # Load memory configuration (optional)
            try:
                with open(MEMORY_CONFIG_FILE, 'r') as f:
                    memory_config = json.load(f)
                    print(f"✅ Loaded memory configuration")
            except FileNotFoundError:
                print(f"⚠️  Memory configuration not found (optional)")
            
            # Load gateway configuration (optional)
            try:
                with open(GATEWAY_CONFIG_FILE, 'r') as f:
                    gateway_config = json.load(f)
                    print(f"✅ Loaded gateway configuration")
            except FileNotFoundError:
                print(f"⚠️  Gateway configuration not found (optional)")
            
            # Load KB configuration (optional)
            try:
                with open(KB_CONFIG_FILE, 'r') as f:
                    kb_config = json.load(f)
                    print(f"✅ Loaded knowledge base configuration")
            except FileNotFoundError:
                print(f"⚠️  Knowledge base configuration not found (optional)")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ ERROR: Configuration file not found: {e}")
            print(f"   Please run 14_full_agent.py first to create the agent")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            print(f"❌ ERROR: Failed to load configurations: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """Set up environment variables for testing."""
        print("\n" + "="*80)
        print("Setting Up Environment Variables")
        print("="*80)
        
        try:
            # Set environment variables
            os.environ['AGENT_ID'] = self.agent_id
            os.environ['ALIAS_ID'] = self.alias_id
            os.environ['TEST_USER_ID'] = TEST_USER_ID
            
            if self.memory_id:
                os.environ['MEMORY_ID'] = self.memory_id
            
            if self.gateway_api_id:
                os.environ['GATEWAY_API_ID'] = self.gateway_api_id
            
            if self.kb_id:
                os.environ['KB_ID'] = self.kb_id
            
            print(f"✅ Environment variables set:")
            print(f"   AGENT_ID: {os.environ['AGENT_ID']}")
            print(f"   ALIAS_ID: {os.environ['ALIAS_ID']}")
            print(f"   TEST_USER_ID: {os.environ['TEST_USER_ID']}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to set up environment: {e}")
            return False
    
    def invoke_agent(self, query: str, session_id: str, enable_trace: bool = True) -> Dict:
        """Invoke the Bedrock Agent with a query."""
        print(f"\n{'='*80}")
        print(f"🤖 Query: {query}")
        print(f"{'='*80}\n")
        
        try:
            response = bedrock_agent_runtime.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.alias_id,
                sessionId=session_id,
                inputText=query,
                enableTrace=enable_trace,
                # Enable memory for this session
                memoryId=self.memory_id if self.memory_id else None
            )
            
            # Process streaming response
            full_response = ""
            trace_data = []
            action_groups_used = []
            memory_accessed = False
            
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    chunk_text = chunk['bytes'].decode('utf-8')
                    full_response += chunk_text
                    print(chunk_text, end='', flush=True)
                
                # Capture trace information
                if enable_trace and 'trace' in event:
                    trace = event['trace']
                    trace_data.append(trace)
                    
                    # Check for action group invocations
                    if 'trace' in trace:
                        trace_info = trace['trace']
                        if 'orchestrationTrace' in trace_info:
                            orch = trace_info['orchestrationTrace']
                            if 'invocationInput' in orch:
                                action_input = orch['invocationInput']
                                if 'actionGroupInvocationInput' in action_input:
                                    action_name = action_input['actionGroupInvocationInput'].get('actionGroupName')
                                    if action_name and action_name not in action_groups_used:
                                        action_groups_used.append(action_name)
                            
                            # Check for memory access
                            if 'observation' in orch:
                                obs_type = orch['observation'].get('type', '')
                                if 'memory' in obs_type.lower():
                                    memory_accessed = True
            
            print("\n")
            
            return {
                'text': full_response,
                'success': True,
                'trace_data': trace_data,
                'action_groups_used': action_groups_used,
                'memory_accessed': memory_accessed
            }
            
        except Exception as e:
            error_msg = f"Failed to invoke agent: {str(e)}"
            print(f"❌ ERROR: {error_msg}\n")
            return {
                'text': "",
                'success': False,
                'error': error_msg,
                'trace_data': [],
                'action_groups_used': [],
                'memory_accessed': False
            }
    
    def test_memory_recall(self, response: Dict) -> TestResult:
        """Test if agent remembers customer prefers email."""
        print("\n" + "="*80)
        print("TEST 1: Memory Recall - Customer Prefers Email")
        print("="*80)
        
        response_text = response['text'].lower()
        memory_accessed = response['memory_accessed']
        
        # Check if response mentions email preference
        email_mentioned = (
            'email' in response_text or
            'e-mail' in response_text or
            'electronic mail' in response_text
        )
        
        # Check if memory was accessed
        if memory_accessed:
            print("✅ Memory was accessed during agent invocation")
        else:
            print("⚠️  Memory access not detected in trace")
        
        # Check if email preference is mentioned
        if email_mentioned:
            print("✅ Response mentions email preference")
            passed = True
            message = "Agent successfully recalled customer's email preference from memory"
        else:
            print("⚠️  Response does not explicitly mention email preference")
            passed = False
            message = "Agent did not recall email preference (may not be in memory yet)"
        
        return TestResult(
            name="Memory Recall Test",
            passed=passed,
            message=message,
            details={
                'memory_accessed': memory_accessed,
                'email_mentioned': email_mentioned,
                'response_excerpt': response_text[:200]
            }
        )
    
    def test_eligibility_lookup(self, response: Dict) -> TestResult:
        """Test if agent performs eligibility lookup."""
        print("\n" + "="*80)
        print("TEST 2: Eligibility Lookup")
        print("="*80)
        
        response_text = response['text'].lower()
        action_groups = response['action_groups_used']
        
        # Check if eligibility action group was used
        eligibility_action_used = any(
            'eligibility' in action.lower() 
            for action in action_groups
        )
        
        # Check if response mentions eligibility
        eligibility_mentioned = (
            'eligibility' in response_text or
            'eligible' in response_text or
            'coverage' in response_text or
            'benefits' in response_text
        )
        
        if eligibility_action_used:
            print(f"✅ Eligibility action group was invoked")
            print(f"   Action groups used: {', '.join(action_groups)}")
        else:
            print(f"⚠️  Eligibility action group not detected")
            if action_groups:
                print(f"   Action groups used: {', '.join(action_groups)}")
        
        if eligibility_mentioned:
            print("✅ Response discusses eligibility or benefits")
            passed = True
            message = "Agent successfully performed eligibility lookup"
        else:
            print("⚠️  Response does not discuss eligibility")
            passed = False
            message = "Agent did not perform eligibility lookup"
        
        return TestResult(
            name="Eligibility Lookup Test",
            passed=passed,
            message=message,
            details={
                'action_groups_used': action_groups,
                'eligibility_action_used': eligibility_action_used,
                'eligibility_mentioned': eligibility_mentioned
            }
        )
    
    def test_personalized_response(self, response: Dict) -> TestResult:
        """Test if agent combines memory and eligibility for personalized response."""
        print("\n" + "="*80)
        print("TEST 3: Personalized Response")
        print("="*80)
        
        response_text = response['text'].lower()
        memory_accessed = response['memory_accessed']
        action_groups = response['action_groups_used']
        
        # Check for personalization indicators
        personalization_indicators = [
            'you' in response_text,  # Direct address
            'your' in response_text,  # Possessive
            TEST_USER_ID.lower() in response_text,  # User ID mentioned
            'prefer' in response_text,  # Preference mentioned
            'remember' in response_text  # Memory reference
        ]
        
        personalization_score = sum(personalization_indicators)
        
        # Check if both memory and action groups were used
        combined_features = memory_accessed and len(action_groups) > 0
        
        if combined_features:
            print("✅ Agent combined memory and action groups")
            print(f"   Memory accessed: {memory_accessed}")
            print(f"   Action groups used: {len(action_groups)}")
        else:
            print("⚠️  Agent did not fully combine features")
            print(f"   Memory accessed: {memory_accessed}")
            print(f"   Action groups used: {len(action_groups)}")
        
        if personalization_score >= 3:
            print(f"✅ Response shows high personalization (score: {personalization_score}/5)")
            passed = True
            message = "Agent provided personalized response combining memory and eligibility"
        elif personalization_score >= 2:
            print(f"⚠️  Response shows moderate personalization (score: {personalization_score}/5)")
            passed = True
            message = "Agent provided somewhat personalized response"
        else:
            print(f"❌ Response shows low personalization (score: {personalization_score}/5)")
            passed = False
            message = "Agent did not provide sufficiently personalized response"
        
        return TestResult(
            name="Personalized Response Test",
            passed=passed,
            message=message,
            details={
                'personalization_score': personalization_score,
                'combined_features': combined_features,
                'memory_accessed': memory_accessed,
                'action_groups_count': len(action_groups)
            }
        )
    
    def run_test(self) -> bool:
        """Run the complete test suite."""
        print("\n" + "="*80)
        print("Full-Featured Agent Test Suite")
        print("="*80)
        print(f"Test User: {TEST_USER_ID}")
        print(f"Test Query: {TEST_QUERY}")
        print("="*80)
        
        # Generate session ID
        session_id = f'test-{TEST_USER_ID}-{int(time.time())}'
        print(f"\nSession ID: {session_id}")
        
        # Invoke agent with test query
        print("\n" + "="*80)
        print("Invoking Agent")
        print("="*80)
        
        response = self.invoke_agent(TEST_QUERY, session_id, enable_trace=True)
        
        if not response['success']:
            print(f"\n❌ Agent invocation failed: {response.get('error')}")
            return False
        
        # Run tests
        test1 = self.test_memory_recall(response)
        self.test_results.append(test1)
        
        test2 = self.test_eligibility_lookup(response)
        self.test_results.append(test2)
        
        test3 = self.test_personalized_response(response)
        self.test_results.append(test3)
        
        # Display test summary
        self.display_test_summary(response, session_id)
        
        # Save test results
        self.save_test_results(response, session_id)
        
        # Return overall pass/fail
        all_passed = all(result.passed for result in self.test_results)
        return all_passed
    
    def display_test_summary(self, response: Dict, session_id: str):
        """Display test results summary."""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        passed_count = sum(1 for result in self.test_results if result.passed)
        total_count = len(self.test_results)
        
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"\n{i}. {result.name}: {status}")
            print(f"   {result.message}")
        
        print("\n" + "="*80)
        print(f"Overall: {passed_count}/{total_count} tests passed")
        print("="*80)
        
        # Display agent response
        print("\n" + "="*80)
        print("AGENT RESPONSE")
        print("="*80)
        print(response['text'])
        print("="*80)
        
        # Display trace summary
        if response['action_groups_used']:
            print("\n📊 Action Groups Used:")
            for action in response['action_groups_used']:
                print(f"  • {action}")
        
        if response['memory_accessed']:
            print("\n💾 Memory: Accessed")
        else:
            print("\n💾 Memory: Not accessed")
    
    def save_test_results(self, response: Dict, session_id: str):
        """Save test results to JSON file."""
        results = {
            'test_timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'test_user': TEST_USER_ID,
            'test_query': TEST_QUERY,
            'agent_config': {
                'agent_id': self.agent_id,
                'alias_id': self.alias_id,
                'memory_id': self.memory_id,
                'gateway_api_id': self.gateway_api_id,
                'kb_id': self.kb_id
            },
            'agent_response': {
                'text': response['text'],
                'success': response['success'],
                'action_groups_used': response['action_groups_used'],
                'memory_accessed': response['memory_accessed']
            },
            'test_results': [
                {
                    'name': result.name,
                    'passed': result.passed,
                    'message': result.message,
                    'details': result.details,
                    'timestamp': result.timestamp
                }
                for result in self.test_results
            ],
            'summary': {
                'total_tests': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r.passed),
                'failed': sum(1 for r in self.test_results if not r.passed)
            }
        }
        
        results_file = f'test_results_full_agent_{session_id}.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to: {results_file}")


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("Full-Featured Member Liability Agent - Test Suite")
    print("="*80)
    print("Testing agent with memory and gateway integration")
    print("="*80)
    
    try:
        # Create tester
        tester = AgentTester()
        
        # Load configurations
        if not tester.load_configurations():
            print("\n❌ Failed to load configurations")
            sys.exit(1)
        
        # Set up environment
        if not tester.setup_environment():
            print("\n❌ Failed to set up environment")
            sys.exit(1)
        
        # Run test
        success = tester.run_test()
        
        if success:
            print("\n" + "="*80)
            print("✅ ALL TESTS PASSED!")
            print("="*80)
            print("\nThe full-featured agent successfully:")
            print("  1. Remembered customer preferences from memory")
            print("  2. Performed eligibility lookup")
            print("  3. Combined both for a personalized response")
            sys.exit(0)
        else:
            print("\n" + "="*80)
            print("⚠️  SOME TESTS FAILED")
            print("="*80)
            print("\nReview the test results above for details.")
            print("Note: Memory may need to be seeded first (run 04_seed_memory.py)")
            sys.exit(1)
        
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
