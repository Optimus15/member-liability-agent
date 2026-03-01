#!/usr/bin/env python3
"""
Benefits Member Liability Agent - AWS Bedrock Agent Setup
This script creates a Bedrock Agent with Knowledge Base integration and custom tools.

NOTE: This script generates the agent configuration. You'll need to:
1. Set up AWS credentials
2. Deploy the Lambda functions for custom tools
3. Create the Knowledge Base in AWS Bedrock
4. Run this script to create the agent
"""

import json
import boto3
import os
from typing import Dict, Optional
from datetime import datetime

# AWS Clients
cfn_client = boto3.client('cloudformation')
bedrock_agent_client = boto3.client('bedrock-agent')
iam_client = boto3.client('iam')

# Configuration
KB_CONFIG_FILE = 'kb_config.json'
CLOUDFORMATION_STACK_NAME = 'knowledgebase'
KB_OUTPUT_KEY = 'KnowledgeBaseId'
PLACEHOLDER_KB_ID = '<PLACE-YOUR-KB-ID>'


def get_knowledge_base_id() -> str:
    """
    Retrieve Knowledge Base ID from CloudFormation stack.
    Falls back to placeholder if retrieval fails.
    """
    try:
        print(f"Attempting to retrieve Knowledge Base ID from CloudFormation stack: {CLOUDFORMATION_STACK_NAME}")
        response = cfn_client.describe_stacks(StackName=CLOUDFORMATION_STACK_NAME)
        
        if not response['Stacks']:
            print(f"WARNING: Stack {CLOUDFORMATION_STACK_NAME} not found")
            return PLACEHOLDER_KB_ID
        
        stack = response['Stacks'][0]
        outputs = stack.get('Outputs', [])
        
        for output in outputs:
            if output['OutputKey'] == KB_OUTPUT_KEY:
                kb_id = output['OutputValue']
                print(f"✓ Successfully retrieved Knowledge Base ID: {kb_id}")
                return kb_id
        
        print(f"WARNING: Output key {KB_OUTPUT_KEY} not found in stack outputs")
        return PLACEHOLDER_KB_ID

    except Exception as e:
        print(f"ERROR: Failed to retrieve Knowledge Base ID from CloudFormation: {str(e)}")
        print(f"Using placeholder: {PLACEHOLDER_KB_ID}")
        return PLACEHOLDER_KB_ID


def save_kb_config(kb_id: str) -> None:
    """Save Knowledge Base configuration to JSON file."""
    config = {
        'knowledge_base_id': kb_id,
        'created_at': datetime.now().isoformat(),
        'source': 'cloudformation' if kb_id != PLACEHOLDER_KB_ID else 'placeholder'
    }
    
    with open(KB_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Saved Knowledge Base configuration to {KB_CONFIG_FILE}")


def create_agent_role() -> str:
    """
    Create IAM role for Bedrock Agent.
    NOTE: This requires appropriate IAM permissions.
    """
    role_name = 'BenefitsMemberLiabilityAgentRole'
    
    # Trust policy for Bedrock Agent
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:Retrieve"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": "arn:aws:lambda:*:*:function:member-liability-*"
            }
        ]
    }
    
    try:
        # Create role
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='IAM role for Benefits Member Liability Bedrock Agent'
        )
        role_arn = response['Role']['Arn']
        
        # Attach inline policy
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockAgentPermissions',
            PolicyDocument=json.dumps(permissions_policy)
        )
        
        print(f"✓ Created IAM role: {role_arn}")
        return role_arn
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"✓ Using existing IAM role: {role_arn}")
        return role_arn
    except Exception as e:
        print(f"ERROR: Failed to create IAM role: {str(e)}")
        print("NOTE: You'll need to create the IAM role manually and update the agent configuration")
        # Return placeholder ARN
        return "arn:aws:iam::ACCOUNT_ID:role/BenefitsMemberLiabilityAgentRole"



def get_action_group_definitions() -> list:
    """
    Define custom tools (action groups) for the agent.
    These tools will be implemented as Lambda functions.
    """
    return [
        {
            'actionGroupName': 'check_eligibility',
            'description': 'Checks member eligibility for benefits and returns coverage information',
            'actionGroupExecutor': {
                'lambda': 'arn:aws:lambda:REGION:ACCOUNT_ID:function:member-liability-check-eligibility'
                # NOTE: Replace with actual Lambda ARN after deployment
            },
            'apiSchema': {
                'payload': json.dumps({
                    'openapi': '3.0.0',
                    'info': {
                        'title': 'Member Eligibility Check API',
                        'version': '1.0.0',
                        'description': 'API for checking member eligibility and benefits'
                    },
                    'paths': {
                        '/check-eligibility': {
                            'post': {
                                'summary': 'Check member eligibility',
                                'description': 'Verifies member eligibility for benefits based on enrollment status and coverage periods',
                                'operationId': 'checkEligibility',
                                'requestBody': {
                                    'required': True,
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'required': ['memberId', 'serviceDate'],
                                                'properties': {
                                                    'memberId': {
                                                        'type': 'string',
                                                        'description': 'Unique member identifier'
                                                    },
                                                    'serviceDate': {
                                                        'type': 'string',
                                                        'format': 'date',
                                                        'description': 'Date of service (YYYY-MM-DD)'
                                                    },
                                                    'benefitCode': {
                                                        'type': 'string',
                                                        'description': 'Optional benefit code to check'
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                'responses': {
                                    '200': {
                                        'description': 'Eligibility check result',
                                        'content': {
                                            'application/json': {
                                                'schema': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'isEligible': {'type': 'boolean'},
                                                        'enrollmentStatus': {'type': 'string'},
                                                        'coveragePeriod': {
                                                            'type': 'object',
                                                            'properties': {
                                                                'startDate': {'type': 'string'},
                                                                'endDate': {'type': 'string'}
                                                            }
                                                        },
                                                        'applicablePolicyRules': {'type': 'array'},
                                                        'ineligibilityReason': {'type': 'string'},
                                                        'reasonCode': {'type': 'string'}
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
            'description': 'Calculates member liability amounts including deductibles, copays, coinsurance, and out-of-pocket maximums',
            'actionGroupExecutor': {
                'lambda': 'arn:aws:lambda:REGION:ACCOUNT_ID:function:member-liability-calculate'
                # NOTE: Replace with actual Lambda ARN after deployment
            },
            'apiSchema': {
                'payload': json.dumps({
                    'openapi': '3.0.0',
                    'info': {
                        'title': 'Member Liability Calculation API',
                        'version': '1.0.0',
                        'description': 'API for calculating member liability amounts'
                    },
                    'paths': {
                        '/calculate-liability': {
                            'post': {
                                'summary': 'Calculate member liability',
                                'description': 'Calculates total member liability with breakdown of deductible, copay, coinsurance, and OOP max',
                                'operationId': 'calculateLiability',
                                'requestBody': {
                                    'required': True,
                                    'content': {
                                        'application/json': {
                                            'schema': {
                                                'type': 'object',
                                                'required': ['memberId', 'claimId'],
                                                'properties': {
                                                    'memberId': {
                                                        'type': 'string',
                                                        'description': 'Unique member identifier'
                                                    },
                                                    'claimId': {
                                                        'type': 'string',
                                                        'description': 'Unique claim identifier'
                                                    },
                                                    'serviceCode': {
                                                        'type': 'string',
                                                        'description': 'Service code for the claim'
                                                    },
                                                    'totalCharges': {
                                                        'type': 'number',
                                                        'description': 'Total charges in dollars'
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                'responses': {
                                    '200': {
                                        'description': 'Liability calculation result',
                                        'content': {
                                            'application/json': {
                                                'schema': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'totalLiability': {'type': 'number'},
                                                        'breakdown': {
                                                            'type': 'object',
                                                            'properties': {
                                                                'deductibleAmount': {'type': 'number'},
                                                                'copayAmount': {'type': 'number'},
                                                                'coinsuranceAmount': {'type': 'number'},
                                                                'outOfPocketApplied': {'type': 'number'},
                                                                'remainingDeductible': {'type': 'number'},
                                                                'remainingOutOfPocket': {'type': 'number'}
                                                            }
                                                        },
                                                        'calculationSteps': {'type': 'array'},
                                                        'appliedRules': {'type': 'array'}
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



def create_bedrock_agent(kb_id: str, role_arn: str) -> Dict:
    """
    Create Bedrock Agent with Knowledge Base integration and custom tools.
    
    NOTE: This requires:
    - AWS Bedrock service enabled in your region
    - Knowledge Base already created
    - Lambda functions deployed for custom tools
    """
    agent_name = 'benefits-member-liability-agent'
    
    # Agent instruction (system prompt)
    agent_instruction = """
You are the Benefits and Member Liability Agent, an expert assistant for healthcare benefits 
eligibility verification and member liability calculations.

Your capabilities:
1. Check member eligibility for benefits based on enrollment status and coverage periods
2. Calculate accurate member liability amounts including deductibles, copays, coinsurance, and out-of-pocket maximums
3. Access knowledge base for policy rules, plan details, and benefits information
4. Provide transparent calculation breakdowns with audit trails

When responding to queries:
- Always verify member eligibility before calculating liability
- Provide clear breakdowns of all liability components
- Reference applicable policy rules and plan details
- Explain calculations in user-friendly terms
- Include relevant dates and coverage period information

For eligibility checks:
- Verify enrollment status (ACTIVE, INACTIVE, SUSPENDED, TERMINATED)
- Confirm service date falls within coverage period
- Return applicable policy rules for the member's plan
- Provide clear ineligibility reasons with codes if not eligible

For liability calculations:
- Calculate remaining deductible from historical claims
- Apply copay based on service type
- Calculate coinsurance after deductible is met
- Enforce out-of-pocket maximum limits
- Ensure component sum equals total liability
- Provide step-by-step calculation audit trail

Always prioritize accuracy and compliance with policy rules.
"""
    
    try:
        print(f"Creating Bedrock Agent: {agent_name}")
        
        # Create agent
        response = bedrock_agent_client.create_agent(
            agentName=agent_name,
            agentResourceRoleArn=role_arn,
            description='Benefits and Member Liability Agent for healthcare eligibility and liability calculations',
            instruction=agent_instruction,
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',  # Using Claude 3 Sonnet
            idleSessionTTLInSeconds=1800  # 30 minutes
        )
        
        agent_id = response['agent']['agentId']
        agent_arn = response['agent']['agentArn']
        print(f"✓ Created agent: {agent_id}")
        
        # Add action groups (custom tools)
        action_groups = get_action_group_definitions()
        
        for action_group in action_groups:
            try:
                print(f"Adding action group: {action_group['actionGroupName']}")
                bedrock_agent_client.create_agent_action_group(
                    agentId=agent_id,
                    agentVersion='DRAFT',
                    actionGroupName=action_group['actionGroupName'],
                    description=action_group['description'],
                    actionGroupExecutor=action_group['actionGroupExecutor'],
                    apiSchema=action_group['apiSchema']
                )
                print(f"✓ Added action group: {action_group['actionGroupName']}")
            except Exception as e:
                print(f"ERROR: Failed to add action group {action_group['actionGroupName']}: {str(e)}")
                print("NOTE: You'll need to add this action group manually in the AWS Console")

        
        # Associate Knowledge Base (if not placeholder)
        if kb_id != PLACEHOLDER_KB_ID:
            try:
                print(f"Associating Knowledge Base: {kb_id}")
                bedrock_agent_client.associate_agent_knowledge_base(
                    agentId=agent_id,
                    agentVersion='DRAFT',
                    knowledgeBaseId=kb_id,
                    description='Benefits policy rules, plan details, and coverage information',
                    knowledgeBaseState='ENABLED'
                )
                print(f"✓ Associated Knowledge Base: {kb_id}")
            except Exception as e:
                print(f"ERROR: Failed to associate Knowledge Base: {str(e)}")
                print("NOTE: You'll need to associate the Knowledge Base manually in the AWS Console")
        else:
            print(f"WARNING: Skipping Knowledge Base association (placeholder ID)")
            print("NOTE: Update kb_config.json with actual KB ID and associate manually")
        
        # Prepare agent (creates agent version)
        print("Preparing agent...")
        prepare_response = bedrock_agent_client.prepare_agent(agentId=agent_id)
        agent_status = prepare_response['agentStatus']
        print(f"✓ Agent prepared with status: {agent_status}")
        
        # Create agent alias
        print("Creating agent alias...")
        alias_response = bedrock_agent_client.create_agent_alias(
            agentId=agent_id,
            agentAliasName='production',
            description='Production alias for Benefits Member Liability Agent'
        )
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"✓ Created agent alias: {alias_id}")
        
        return {
            'agent_id': agent_id,
            'agent_arn': agent_arn,
            'alias_id': alias_id,
            'status': agent_status,
            'knowledge_base_id': kb_id
        }
        
    except Exception as e:
        print(f"ERROR: Failed to create Bedrock Agent: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Ensure AWS Bedrock is enabled in your region")
        print("2. Verify IAM role has correct permissions")
        print("3. Check that Knowledge Base exists and is accessible")
        print("4. Ensure Lambda functions are deployed")
        print("5. Review CloudWatch logs for detailed error messages")
        raise


def save_agent_config(agent_info: Dict) -> None:
    """Save agent configuration to JSON file."""
    config_file = 'agent_config.json'
    
    config = {
        'agent_id': agent_info['agent_id'],
        'agent_arn': agent_info['agent_arn'],
        'alias_id': agent_info['alias_id'],
        'status': agent_info['status'],
        'knowledge_base_id': agent_info['knowledge_base_id'],
        'created_at': datetime.now().isoformat(),
        'action_groups': [
            'check_eligibility',
            'calculate_member_liability'
        ]
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Saved agent configuration to {config_file}")



def main():
    """Main execution flow."""
    print("=" * 80)
    print("Benefits Member Liability Agent - Setup")
    print("=" * 80)
    print()
    
    # Step 1: Retrieve Knowledge Base ID
    print("Step 1: Retrieving Knowledge Base ID...")
    kb_id = get_knowledge_base_id()
    print()
    
    # Step 2: Save KB configuration
    print("Step 2: Saving Knowledge Base configuration...")
    save_kb_config(kb_id)
    print()
    
    # Step 3: Create IAM role
    print("Step 3: Creating IAM role for agent...")
    try:
        role_arn = create_agent_role()
    except Exception as e:
        print(f"WARNING: Could not create IAM role automatically: {str(e)}")
        print("Please create the role manually and update the script with the ARN")
        return
    print()
    
    # Step 4: Create Bedrock Agent
    print("Step 4: Creating Bedrock Agent with Knowledge Base and custom tools...")
    try:
        agent_info = create_bedrock_agent(kb_id, role_arn)
        print()
        
        # Step 5: Save agent configuration
        print("Step 5: Saving agent configuration...")
        save_agent_config(agent_info)
        print()
        
        # Success summary
        print("=" * 80)
        print("✓ SUCCESS: Agent created successfully!")
        print("=" * 80)
        print(f"Agent ID: {agent_info['agent_id']}")
        print(f"Agent ARN: {agent_info['agent_arn']}")
        print(f"Alias ID: {agent_info['alias_id']}")
        print(f"Knowledge Base ID: {agent_info['knowledge_base_id']}")
        print()
        print("Next steps:")
        print("1. Deploy Lambda functions for custom tools:")
        print("   - member-liability-check-eligibility")
        print("   - member-liability-calculate")
        print("2. Update action group Lambda ARNs in AWS Console")
        print("3. Test the agent using AWS Console or SDK")
        print("4. Monitor CloudWatch logs for debugging")
        
    except Exception as e:
        print(f"\n❌ FAILED: Could not create agent")
        print(f"Error: {str(e)}")
        print("\nPlease review the error messages above and follow troubleshooting steps")


if __name__ == '__main__':
    main()
