"""
Lambda Function: Check Member Eligibility
This function checks member eligibility for benefits based on enrollment status and coverage periods.

NOTE: This is a template implementation. You'll need to:
1. Connect to your actual member database
2. Implement real policy rule retrieval
3. Add error handling and logging
4. Deploy to AWS Lambda
"""

import json
import boto3
from datetime import datetime
from typing import Dict, Any

# NOTE: Replace with your actual database/service connections
# dynamodb = boto3.resource('dynamodb')
# members_table = dynamodb.Table('members')


def parse_date(date_string: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    return datetime.strptime(date_string, '%Y-%m-%d')


def check_eligibility(member_id: str, service_date: str, benefit_code: str = None) -> Dict[str, Any]:
    """
    Check member eligibility for benefits.
    
    Args:
        member_id: Unique member identifier
        service_date: Date of service (YYYY-MM-DD)
        benefit_code: Optional benefit code to check
    
    Returns:
        Eligibility result with enrollment status and applicable policy rules
    """
    
    # NOTE: This is mock data - replace with actual database queries
    # In production, you would:
    # 1. Query member from database
    # 2. Retrieve enrollment status
    # 3. Get coverage period
    # 4. Fetch applicable policy rules
    
    # Mock member data
    mock_member = {
        'memberId': member_id,
        'enrollmentStatus': 'ACTIVE',
        'coveragePeriod': {
            'startDate': '2024-01-01',
            'endDate': '2024-12-31'
        },
        'planId': 'PPO-001'
    }
    
    # Parse service date
    service_dt = parse_date(service_date)
    coverage_start = parse_date(mock_member['coveragePeriod']['startDate'])
    coverage_end = parse_date(mock_member['coveragePeriod']['endDate'])
    
    # Check enrollment status
    if mock_member['enrollmentStatus'] != 'ACTIVE':
        return {
            'isEligible': False,
            'memberId': member_id,
            'serviceDate': service_date,
            'enrollmentStatus': mock_member['enrollmentStatus'],
            'ineligibilityReason': 'Member is not actively enrolled',
            'reasonCode': 'NOT_ENROLLED'
        }
    
    # Check if service date is within coverage period
    if not (coverage_start <= service_dt <= coverage_end):
        return {
            'isEligible': False,
            'memberId': member_id,
            'serviceDate': service_date,
            'enrollmentStatus': mock_member['enrollmentStatus'],
            'coveragePeriod': mock_member['coveragePeriod'],
            'ineligibilityReason': f'Service date {service_date} is outside coverage period',
            'reasonCode': 'OUTSIDE_COVERAGE_PERIOD'
        }
    
    # Member is eligible - return applicable policy rules
    # NOTE: In production, fetch actual policy rules from database
    mock_policy_rules = [
        {
            'ruleId': 'RULE-001',
            'planId': 'PPO-001',
            'priority': 1,
            'name': 'Standard Deductible',
            'description': 'Apply $1000 annual deductible',
            'actionType': 'APPLY_DEDUCTIBLE'
        },
        {
            'ruleId': 'RULE-002',
            'planId': 'PPO-001',
            'priority': 2,
            'name': 'Primary Care Copay',
            'description': 'Apply $25 copay for primary care visits',
            'actionType': 'SET_COPAY'
        }
    ]
    
    return {
        'isEligible': True,
        'memberId': member_id,
        'serviceDate': service_date,
        'enrollmentStatus': mock_member['enrollmentStatus'],
        'coveragePeriod': mock_member['coveragePeriod'],
        'applicablePolicyRules': mock_policy_rules
    }


def lambda_handler(event, context):
    """
    AWS Lambda handler for Bedrock Agent action group.
    
    Event structure from Bedrock Agent:
    {
        "messageVersion": "1.0",
        "agent": {...},
        "inputText": "...",
        "sessionId": "...",
        "actionGroup": "check_eligibility",
        "apiPath": "/check-eligibility",
        "httpMethod": "POST",
        "parameters": [
            {"name": "memberId", "type": "string", "value": "M123456"},
            {"name": "serviceDate", "type": "string", "value": "2024-03-15"},
            {"name": "benefitCode", "type": "string", "value": "PRIMARY_CARE"}
        ]
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract parameters from Bedrock Agent event
        parameters = {param['name']: param['value'] for param in event.get('parameters', [])}
        
        member_id = parameters.get('memberId')
        service_date = parameters.get('serviceDate')
        benefit_code = parameters.get('benefitCode')
        
        # Validate required parameters
        if not member_id or not service_date:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event['actionGroup'],
                    'apiPath': event['apiPath'],
                    'httpMethod': event['httpMethod'],
                    'httpStatusCode': 400,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({
                                'error': 'Missing required parameters: memberId and serviceDate'
                            })
                        }
                    }
                }
            }
        
        # Check eligibility
        result = check_eligibility(member_id, service_date, benefit_code)
        
        # Return response in Bedrock Agent format
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'apiPath': event['apiPath'],
                'httpMethod': event['httpMethod'],
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'check_eligibility'),
                'apiPath': event.get('apiPath', '/check-eligibility'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({
                            'error': f'Internal server error: {str(e)}'
                        })
                    }
                }
            }
        }
