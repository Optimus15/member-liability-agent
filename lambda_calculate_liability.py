"""
Lambda Function: Calculate Member Liability
This function calculates member liability amounts including deductibles, copays, coinsurance, and OOP max.

NOTE: This is a template implementation. You'll need to:
1. Connect to your actual claims database
2. Implement real liability calculation logic
3. Add error handling and logging
4. Deploy to AWS Lambda
"""

import json
import boto3
from typing import Dict, Any, List
from datetime import datetime

# NOTE: Replace with your actual database/service connections
# dynamodb = boto3.resource('dynamodb')
# claims_table = dynamodb.Table('claims')
# members_table = dynamodb.Table('members')


def get_member_data(member_id: str) -> Dict[str, Any]:
    """
    Retrieve member data including plan details and deductible/OOP max.
    NOTE: Replace with actual database query.
    """
    # Mock member data
    return {
        'memberId': member_id,
        'planId': 'PPO-001',
        'deductible': 100000,  # $1000 in cents
        'outOfPocketMaximum': 500000,  # $5000 in cents
        'deductiblePaid': 50000,  # $500 already paid
        'totalPaid': 150000  # $1500 total paid this year
    }


def get_claim_data(claim_id: str) -> Dict[str, Any]:
    """
    Retrieve claim data.
    NOTE: Replace with actual database query.
    """
    # Mock claim data
    return {
        'claimId': claim_id,
        'serviceCode': 'PRIMARY_CARE',
        'serviceCategory': 'OFFICE_VISIT',
        'totalCharges': 15000  # $150 in cents
    }


def get_policy_rules(plan_id: str, service_code: str) -> List[Dict[str, Any]]:
    """
    Retrieve applicable policy rules for the plan and service.
    NOTE: Replace with actual database query.
    """
    # Mock policy rules
    return [
        {
            'ruleId': 'RULE-002',
            'actionType': 'SET_COPAY',
            'parameters': {'amount': 2500}  # $25 copay
        },
        {
            'ruleId': 'RULE-003',
            'actionType': 'SET_COINSURANCE',
            'parameters': {'percentage': 0.20}  # 20% coinsurance
        }
    ]


def calculate_liability(member_id: str, claim_id: str, service_code: str = None, 
                       total_charges: float = None) -> Dict[str, Any]:
    """
    Calculate member liability with breakdown.
    
    Args:
        member_id: Unique member identifier
        claim_id: Unique claim identifier
        service_code: Service code for the claim
        total_charges: Total charges in dollars
    
    Returns:
        Liability calculation result with breakdown and audit trail
    """
    
    # Get member and claim data
    member = get_member_data(member_id)
    claim = get_claim_data(claim_id)
    
    # Override with provided values if present
    if service_code:
        claim['serviceCode'] = service_code
    if total_charges:
        claim['totalCharges'] = int(total_charges * 100)  # Convert to cents
    
    # Get applicable policy rules
    policy_rules = get_policy_rules(member['planId'], claim['serviceCode'])
    
    # Initialize calculation components
    deductible_amount = 0
    copay_amount = 0
    coinsurance_amount = 0
    out_of_pocket_applied = 0
    
    calculation_steps = []
    step_number = 1
    
    # Step 1: Calculate remaining deductible
    remaining_deductible = max(0, member['deductible'] - member['deductiblePaid'])
    calculation_steps.append({
        'stepNumber': step_number,
        'operation': 'Calculate remaining deductible',
        'inputValues': {
            'totalDeductible': member['deductible'] / 100,
            'deductiblePaid': member['deductiblePaid'] / 100
        },
        'outputValue': remaining_deductible / 100,
        'timestamp': datetime.now().isoformat()
    })
    step_number += 1
    
    # Step 2: Apply copay (if applicable)
    copay_rule = next((r for r in policy_rules if r['actionType'] == 'SET_COPAY'), None)
    if copay_rule:
        copay_amount = copay_rule['parameters']['amount']
        calculation_steps.append({
            'stepNumber': step_number,
            'operation': 'Apply copay',
            'inputValues': {'serviceCode': claim['serviceCode']},
            'outputValue': copay_amount / 100,
            'appliedRule': copay_rule['ruleId'],
            'timestamp': datetime.now().isoformat()
        })
        step_number += 1
    
    # Step 3: Apply deductible to remaining charges
    charges_after_copay = claim['totalCharges'] - copay_amount
    if remaining_deductible > 0:
        deductible_amount = min(remaining_deductible, charges_after_copay)
        calculation_steps.append({
            'stepNumber': step_number,
            'operation': 'Apply deductible',
            'inputValues': {
                'chargesAfterCopay': charges_after_copay / 100,
                'remainingDeductible': remaining_deductible / 100
            },
            'outputValue': deductible_amount / 100,
            'timestamp': datetime.now().isoformat()
        })
        step_number += 1
    
    # Step 4: Apply coinsurance (if deductible is met)
    charges_after_deductible = charges_after_copay - deductible_amount
    coinsurance_rule = next((r for r in policy_rules if r['actionType'] == 'SET_COINSURANCE'), None)
    if coinsurance_rule and charges_after_deductible > 0:
        coinsurance_percentage = coinsurance_rule['parameters']['percentage']
        coinsurance_amount = int(charges_after_deductible * coinsurance_percentage)
        calculation_steps.append({
            'stepNumber': step_number,
            'operation': 'Apply coinsurance',
            'inputValues': {
                'chargesAfterDeductible': charges_after_deductible / 100,
                'coinsurancePercentage': coinsurance_percentage
            },
            'outputValue': coinsurance_amount / 100,
            'appliedRule': coinsurance_rule['ruleId'],
            'timestamp': datetime.now().isoformat()
        })
        step_number += 1
    
    # Step 5: Calculate total liability before OOP max
    total_liability_before_oop = copay_amount + deductible_amount + coinsurance_amount
    calculation_steps.append({
        'stepNumber': step_number,
        'operation': 'Sum liability components',
        'inputValues': {
            'copay': copay_amount / 100,
            'deductible': deductible_amount / 100,
            'coinsurance': coinsurance_amount / 100
        },
        'outputValue': total_liability_before_oop / 100,
        'timestamp': datetime.now().isoformat()
    })
    step_number += 1
    
    # Step 6: Apply out-of-pocket maximum
    remaining_oop = max(0, member['outOfPocketMaximum'] - member['totalPaid'])
    total_liability = min(total_liability_before_oop, remaining_oop)
    
    if total_liability < total_liability_before_oop:
        out_of_pocket_applied = total_liability_before_oop - total_liability
        calculation_steps.append({
            'stepNumber': step_number,
            'operation': 'Apply out-of-pocket maximum cap',
            'inputValues': {
                'liabilityBeforeOOP': total_liability_before_oop / 100,
                'remainingOOP': remaining_oop / 100
            },
            'outputValue': total_liability / 100,
            'timestamp': datetime.now().isoformat()
        })
    
    # Calculate remaining amounts
    new_remaining_deductible = max(0, remaining_deductible - deductible_amount)
    new_remaining_oop = max(0, remaining_oop - total_liability)
    
    return {
        'totalLiability': total_liability / 100,  # Convert back to dollars
        'breakdown': {
            'deductibleAmount': deductible_amount / 100,
            'copayAmount': copay_amount / 100,
            'coinsuranceAmount': coinsurance_amount / 100,
            'outOfPocketApplied': out_of_pocket_applied / 100,
            'remainingDeductible': new_remaining_deductible / 100,
            'remainingOutOfPocket': new_remaining_oop / 100
        },
        'calculationSteps': calculation_steps,
        'appliedRules': [r['ruleId'] for r in policy_rules],
        'timestamp': datetime.now().isoformat()
    }


def lambda_handler(event, context):
    """
    AWS Lambda handler for Bedrock Agent action group.
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract parameters from Bedrock Agent event
        parameters = {param['name']: param['value'] for param in event.get('parameters', [])}
        
        member_id = parameters.get('memberId')
        claim_id = parameters.get('claimId')
        service_code = parameters.get('serviceCode')
        total_charges = parameters.get('totalCharges')
        
        # Convert total_charges to float if present
        if total_charges:
            total_charges = float(total_charges)
        
        # Validate required parameters
        if not member_id or not claim_id:
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
                                'error': 'Missing required parameters: memberId and claimId'
                            })
                        }
                    }
                }
            }
        
        # Calculate liability
        result = calculate_liability(member_id, claim_id, service_code, total_charges)
        
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
                'actionGroup': event.get('actionGroup', 'calculate_member_liability'),
                'apiPath': event.get('apiPath', '/calculate-liability'),
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
