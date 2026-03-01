#!/usr/bin/env python3
"""
Full-Featured Member Liability Agent with Memory and Gateway Integration
This script creates a complete Bedrock Agent with:
- Memory capabilities (session summary, user preferences, semantic memory)
- API Gateway integration for external access
- Knowledge Base integration
- Custom Lambda tools

Agent Name: full_featured_member_liability_agent
System Prompt: You are a member liability assistant with memory and benefits lookup 
capabilities. Remember customer preferences, look up eligibility and benefit details.

Usage:
    python3 14_full_agent.py
"""

import json
import boto3
import sys
from typing import Dict, Optional
from datetime import datetime

# AWS Clients
bedrock_agent_client = boto3.client('bedrock-agent')
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

# Configuration Files
KB_CONFIG_FILE = 'kb_config.json'
MEMORY_CONFIG_FILE = 'memory_config.json'
GATEWAY_CONFIG_FILE = 'gateway_config.json'
LAMBDA_INTEGRATION_CONFIG_FILE = 'lambda_integration_config.json'
AGENT_CONFIG_FILE = 'full_agent_config.json'

# Agent Configuration
AGENT_NAME = 'full_featured_member_liability_agent'
AGENT_DESCRIPTION = 'Full-featured member liability assistant with memory and benefits lookup capabilities'

# System Prompt
AGENT_INSTRUCTION = """
You are a member liability assistant with memory and benefits lookup capabilities.

Your core capabilities:
1. MEMORY: Remember customer preferences, previous interactions, and conversation history
2. ELIGIBILITY: Look up member eligibility for benefits and coverage
3. LIABILITY CALCULATION: Calculate accurate member liability amounts
4. BENEFITS LOOKUP: Access knowledge base for policy rules and plan details
5. GATEWAY INTEGRATION: Connect to external systems for real-time data

Memory Guidelines:
- Remember customer preferences across sessions
- Recall previous eligibility checks and calculations
- Track conversation history for context
- Use semantic memory to find relevant past interactions
- Personalize responses based on stored preferences

When interacting with customers:
- Greet returning customers by acknowledging previous interactions
- Reference past eligibility checks or calculations when relevant
- Remember preferred communication style and terminology
- Track frequently asked questions for each customer
- Maintain context across multiple sessions

For eligibility checks:
- Verify enrollment status (ACTIVE, INACTIVE, SUSPENDED, TERMINATED)
- Confirm service date falls within coverage period
- Return applicable policy rules for the member's plan
- Provide clear ineligibility reasons with codes if not eligible
- Remember eligibility results for future reference

For liability calculations:
- Calculate remaining deductible from historical claims
- Apply copay based on service type
- Calculate coinsurance after deductible is met
- Enforce out-of-pocket maximum limits
- Provide step-by-step calculation audit trail
- Store calculation results in memory for future reference

For benefits lookup:
- Search knowledge base for policy rules and plan details
- Explain coverage limits and exclusions
- Provide benefit summaries in clear language
- Reference specific policy sections when needed

Always prioritize:
- Accuracy in calculations and eligibility determinations
- Compliance with policy rules and regulations
- Clear, personalized communication
- Maintaining customer context across sessions
- Protecting sensitive member information
"""

# AWS Region
AWS_REGION = None


def get_aws_region() -> str:
    """Get the AWS region from the boto3 session."""
    session = boto3.session.Session()
    region = session.region_name
    
    if not region:
        region = 'us-east-1'
        print(f"⚠️  WARNING: No region configured, defaulting to {region}")
    
    return region


def get_account_id() -> str:
    """Get AWS account ID using STS."""
    try:
        response = sts_client.get_caller_identity()
        return response['Account']
    except Exception as e:
        print(f"\n⚠️  WARNING: Could not get account ID: {str(e)}")
        return '123456789012'  # Placeholder


def load_config_file(filename: str, required: bool = True) -> Optional[Dict]:
    """Load configuration from JSON file."""
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        print(f"✅ Loaded configuration from: {filename}")
        return config
    except FileNotFoundError:
        if required:
            print(f"❌ ERROR: {filename} not found")
            print(f"   Please run the prerequisite scripts first")
            return None
        else:
            print(f"⚠️  WARNING: {filename} not found (optional)")
            return {}
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {filename}: {str(e)}")
        return None


def create_agent_role(account_id: str, region: str) -> str:
    """Create IAM role for Bedrock Agent with all necessary permissions."""
    role_name = 'FullFeaturedMemberLiabilityAgentRole'
    
    print("\n" + "="*80)
    print("Creating IAM Role")
    print("="*80)
    
    # Trust policy for Bedrock Agent
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock:{region}:{account_id}:agent/*"
                    }
                }
            }
        ]
    }
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockInvokeModel",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": f"arn:aws:bedrock:{region}::foundation-model/*"
            },
            {
                "Sid": "BedrockKnowledgeBase",
                "Effect": "Allow",
                "Action": [
                    "bedrock:Retrieve"
                ],
                "Resource": f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/*"
            },
            {
                "Sid": "LambdaInvoke",
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": [
                    f"arn:aws:lambda:{region}:{account_id}:function:member-liability-*",
                    f"arn:aws:lambda:{region}:{account_id}:function:OrderLookupFunction"
                ]
            },
            {
                "Sid": "BedrockAgentMemory",
                "Effect": "Allow",
                "Action": [
                    "bedrock:GetAgentMemory",
                    "bedrock:DeleteAgentMemory"
                ],
                "Resource": f"arn:aws:bedrock:{region}:{account_id}:agent/*"
            }
        ]
    }
    
    try:
        # Create role
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='IAM role for Full-Featured Member Liability Bedrock Agent with memory and gateway'
        )
        role_arn = response['Role']['Arn']
        
        # Attach inline policy
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockAgentFullPermissions',
            PolicyDocument=json.dumps(permissions_policy)
        )
        
        print(f"✅ Created IAM role: {role_arn}")
        return role_arn
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_arn}")
        
        # Update policy
        try:
            iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='BedrockAgentFullPermissions',
                PolicyDocument=json.dumps(permissions_policy)
            )
            print(f"✅ Updated IAM role permissions")
        except Exception as e:
            print(f"⚠️  WARNING: Could not update role permissions: {str(e)}")
        
        return role_arn
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create IAM role: {str(e)}")
        raise


def get_action_group_definitions(account_id: str, region: str, lambda_config: Dict) -> list:
    """Define custom tools (action groups) for the agent."""
    
    action_groups = [
        {
            'actionGroupName': 'check_eligibility',
            'description': 'Checks member eligibility for benefits and returns coverage information',
            'actionGroupExecutor': {
                'lambda': f'arn:aws:lambda:{region}:{account_id}:function:member-liability-check-eligibility'
            },
            'apiSchema': {
                'payload': json.dumps({
                    'openapi': '3.0.0',
                    'info': {
                        'title': 'Member Eligibility Check API',
                        'version': '1.0.0'
                    },
                    'paths': {
                        '/check-eligibility': {
                            'post': {
                                'summary': 'Check member eligibility',
                                'operationId': 'checkEligibility',
                                'requestBody': {
                                    'required': True,
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'required': ['memberId', 'serviceDate'],
                                                'properties': {
                                                    'memberId': {'type': 'string'},
                                                    'serviceDate': {'type': 'string', 'format': 'date'},
                                                    'benefitCode': {'type': 'string'}
                                                }
                                            }
                                        }
                                    }
                                },
                                'responses': {
                                    '200': {
                                        'description': 'Eligibility result',
                                        'content': {
                                            'application/json': {
                                                'schema': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'isEligible': {'type': 'boolean'},
                                                        'enrollmentStatus': {'type': 'string'},
                                                        'coveragePeriod': {'type': 'object'}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                })
            }
        },
        {
            'actionGroupName': 'calculate_member_liability',
            'description': 'Calculates member liability amounts including deductibles, copays, and coinsurance',
            'actionGroupExecutor': {
                'lambda': f'arn:aws:lambda:{region}:{account_id}:function:member-liability-calculate'
            },
            'apiSchema': {
                'payload': json.dumps({
                    'openapi': '3.0.0',
                    'info': {
                        'title': 'Member Liability Calculation API',
                        'version': '1.0.0'
                    },
                    'paths': {
                        '/calculate-liability': {
                            'post': {
                                'summary': 'Calculate member liability',
                                'operationId': 'calculateLiability',
                                'requestBody': {
                                    'required': True,
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'required': ['memberId', 'claimId'],
                                                'properties': {
                                                    'memberId': {'type': 'string'},
                                                    'claimId': {'type': 'string'},
                                                    'serviceCode': {'type': 'string'},
                                                    'totalCharges': {'type': 'number'}
                                                }
                                            }
                                        }
                                    }
                                },
                                'responses': {
                                    '200': {
                                        'description': 'Liability calculation',
                                        'content': {
                                            'application/json': {
                                                'schema': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'totalLiability': {'type': 'number'},
                                                        'breakdown': {'type': 'object'}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                })
            }
        }
    ]
    
    # Add OrderLookup function if available
    if lambda_config and lambda_config.get('function_arn'):
        action_groups.append({
            'actionGroupName': 'order_lookup',
            'description': 'Looks up order information and details',
            'actionGroupExecutor': {
                'lambda': lambda_config['function_arn']
            },
            'apiSchema': {
                'payload': json.dumps({
                    'openapi': '3.0.0',
                    'info': {
                        'title': 'Order Lookup API',
                        'version': '1.0.0'
                    },
                    'paths': {
                        '/order-lookup': {
                            'post': {
                                'summary': 'Look up order details',
                                'operationId': 'orderLookup',
                                'requestBody': {
                                    'required': True,
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'required': ['order_id'],
                                                'properties': {
                                                    'order_id': {'type': 'string'}
                                                }
                                            }
                                        }
                                    }
                                },
                                'responses': {
                                    '200': {
                                        'description': 'Order details',
                                        'content': {
                                            'application/json': {
                                                'schema': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'order_id': {'type': 'string'},
                                                        'status': {'type': 'string'},
                                                        'details': {'type': 'object'}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                })
            }
        })
    
    return action_groups


def create_bedrock_agent(
    role_arn: str,
    kb_config: Dict,
    memory_config: Dict,
    gateway_config: Dict,
    lambda_config: Dict,
    account_id: str,
    region: str
) -> Dict:
    """Create Bedrock Agent with memory and gateway integration."""
    
    print("\n" + "="*80)
    print("Creating Bedrock Agent")
    print("="*80)
    print(f"Agent Name: {AGENT_NAME}")
    print("="*80)
    
    try:
        # Create agent
        response = bedrock_agent_client.create_agent(
            agentName=AGENT_NAME,
            agentResourceRoleArn=role_arn,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
            idleSessionTTLInSeconds=1800  # 30 minutes
        )
        
        agent_id = response['agent']['agentId']
        agent_arn = response['agent']['agentArn']
        print(f"✅ Created agent: {agent_id}")
        
        # Add action groups
        action_groups = get_action_group_definitions(account_id, region, lambda_config)
        
        for action_group in action_groups:
            try:
                print(f"\nAdding action group: {action_group['actionGroupName']}")
                bedrock_agent_client.create_agent_action_group(
                    agentId=agent_id,
                    agentVersion='DRAFT',
                    actionGroupName=action_group['actionGroupName'],
                    description=action_group['description'],
                    actionGroupExecutor=action_group['actionGroupExecutor'],
                    apiSchema=action_group['apiSchema']
                )
                print(f"✅ Added action group: {action_group['actionGroupName']}")
            except Exception as e:
                print(f"⚠️  WARNING: Could not add action group {action_group['actionGroupName']}: {str(e)}")
        
        # Associate Knowledge Base
        if kb_config and kb_config.get('knowledge_base_id'):
            kb_id = kb_config['knowledge_base_id']
            if kb_id and kb_id != '<PLACE-YOUR-KB-ID>':
                try:
                    print(f"\nAssociating Knowledge Base: {kb_id}")
                    bedrock_agent_client.associate_agent_knowledge_base(
                        agentId=agent_id,
                        agentVersion='DRAFT',
                        knowledgeBaseId=kb_id,
                        description='Benefits policy rules and plan details',
                        knowledgeBaseState='ENABLED'
                    )
                    print(f"✅ Associated Knowledge Base: {kb_id}")
                except Exception as e:
                    print(f"⚠️  WARNING: Could not associate Knowledge Base: {str(e)}")
        
        # Configure Memory (if memory config exists)
        if memory_config and memory_config.get('memory_id'):
            try:
                print(f"\nConfiguring agent memory: {memory_config['memory_id']}")
                # Memory is already created, just update agent to use it
                bedrock_agent_client.update_agent(
                    agentId=agent_id,
                    agentName=AGENT_NAME,
                    agentResourceRoleArn=role_arn,
                    description=AGENT_DESCRIPTION,
                    instruction=AGENT_INSTRUCTION,
                    foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
                    memoryConfiguration={
                        'enabledMemoryTypes': ['SESSION_SUMMARY'],
                        'storageDays': 30
                    }
                )
                print(f"✅ Configured agent memory")
            except Exception as e:
                print(f"⚠️  WARNING: Could not configure memory: {str(e)}")
        
        # Prepare agent
        print("\nPreparing agent...")
        prepare_response = bedrock_agent_client.prepare_agent(agentId=agent_id)
        agent_status = prepare_response['agentStatus']
        print(f"✅ Agent prepared with status: {agent_status}")
        
        # Create agent alias
        print("\nCreating agent alias...")
        alias_response = bedrock_agent_client.create_agent_alias(
            agentId=agent_id,
            agentAliasName='production',
            description='Production alias for full-featured member liability agent'
        )
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"✅ Created agent alias: {alias_id}")
        
        return {
            'agent_id': agent_id,
            'agent_arn': agent_arn,
            'alias_id': alias_id,
            'status': agent_status,
            'knowledge_base_id': kb_config.get('knowledge_base_id') if kb_config else None,
            'memory_id': memory_config.get('memory_id') if memory_config else None,
            'gateway_api_id': gateway_config.get('api_id') if gateway_config else None
        }
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create Bedrock Agent: {str(e)}")
        raise


def save_agent_config(agent_info: Dict) -> None:
    """Save agent configuration to JSON file."""
    print("\n" + "="*80)
    print("Saving Agent Configuration")
    print("="*80)
    
    config = {
        'agent_name': AGENT_NAME,
        'agent_id': agent_info['agent_id'],
        'agent_arn': agent_info['agent_arn'],
        'alias_id': agent_info['alias_id'],
        'status': agent_info['status'],
        'knowledge_base_id': agent_info.get('knowledge_base_id'),
        'memory_id': agent_info.get('memory_id'),
        'gateway_api_id': agent_info.get('gateway_api_id'),
        'created_at': datetime.now().isoformat(),
        'features': {
            'memory': agent_info.get('memory_id') is not None,
            'knowledge_base': agent_info.get('knowledge_base_id') is not None,
            'gateway_integration': agent_info.get('gateway_api_id') is not None
        },
        'action_groups': [
            'check_eligibility',
            'calculate_member_liability',
            'order_lookup'
        ]
    }
    
    with open(AGENT_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to: {AGENT_CONFIG_FILE}")


def display_summary(agent_info: Dict, gateway_config: Dict) -> None:
    """Display setup summary and next steps."""
    print("\n" + "="*80)
    print("✅ SUCCESS: Full-Featured Agent Created!")
    print("="*80)
    
    print(f"\nAgent Details:")
    print(f"  Name: {AGENT_NAME}")
    print(f"  ID: {agent_info['agent_id']}")
    print(f"  Alias: {agent_info['alias_id']}")
    print(f"  Status: {agent_info['status']}")
    
    print(f"\nFeatures Enabled:")
    print(f"  ✅ Memory: {'Yes' if agent_info.get('memory_id') else 'No'}")
    print(f"  ✅ Knowledge Base: {'Yes' if agent_info.get('knowledge_base_id') else 'No'}")
    print(f"  ✅ Gateway Integration: {'Yes' if agent_info.get('gateway_api_id') else 'No'}")
    
    if gateway_config and gateway_config.get('api_url'):
        print(f"\nAPI Gateway:")
        print(f"  URL: {gateway_config['api_url']}")
        print(f"  Stage: {gateway_config.get('stage', 'prod')}")
    
    print(f"\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Test the agent:")
    print(f"   python3 02_test_agent.py")
    
    print("\n2. Test memory capabilities:")
    print(f"   python3 05_test_memory.py")
    
    print("\n3. Access via API Gateway:")
    if gateway_config and gateway_config.get('api_url'):
        print(f"   curl -X POST {gateway_config['api_url']}/agent \\")
        print("     -H 'Authorization: Bearer <cognito_token>' \\")
        print("     -d '{\"message\": \"Check eligibility for member 12345\"}'")
    else:
        print("   Configure API Gateway integration first")
    
    print("\n4. Monitor agent:")
    print("   - CloudWatch Logs: /aws/bedrock/agent")
    print("   - Agent metrics in AWS Console")
    print("   - Memory usage and storage")


def main():
    """Main execution."""
    global AWS_REGION
    
    print("\n" + "="*80)
    print("Full-Featured Member Liability Agent Setup")
    print("="*80)
    print("Creating agent with memory and gateway integration")
    print("="*80)
    
    try:
        # Get AWS region and account
        AWS_REGION = get_aws_region()
        account_id = get_account_id()
        print(f"\nAWS Region: {AWS_REGION}")
        print(f"AWS Account: {account_id}")
        
        # Load configuration files
        print("\n" + "="*80)
        print("Loading Configuration Files")
        print("="*80)
        
        kb_config = load_config_file(KB_CONFIG_FILE, required=False)
        memory_config = load_config_file(MEMORY_CONFIG_FILE, required=False)
        gateway_config = load_config_file(GATEWAY_CONFIG_FILE, required=False)
        lambda_config = load_config_file(LAMBDA_CONFIG_FILE, required=False)
        
        # Create IAM role
        role_arn = create_agent_role(account_id, AWS_REGION)
        
        # Create agent
        agent_info = create_bedrock_agent(
            role_arn,
            kb_config,
            memory_config,
            gateway_config,
            lambda_config,
            account_id,
            AWS_REGION
        )
        
        # Save configuration
        save_agent_config(agent_info)
        
        # Display summary
        display_summary(agent_info, gateway_config)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
