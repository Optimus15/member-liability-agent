#!/usr/bin/env python3
"""
Create AWS API Gateway for Member Liability Agent
This script creates a REST API Gateway named ReturnsRefundsGateway with Cognito authentication.

Features:
- Creates REST API Gateway
- Loads Cognito and IAM role configuration
- Configures Cognito authorizer
- Saves gateway ID and URL to gateway_config.json

Usage:
    python3 11_create_gateway.py
"""

import boto3
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Configuration
GATEWAY_NAME = 'ReturnsRefundsGateway'
GATEWAY_DESCRIPTION = 'API Gateway for Member Liability Agent with Cognito authentication'
COGNITO_CONFIG_FILE = 'cognito_config.json'
GATEWAY_ROLE_CONFIG_FILE = 'gateway_role_config.json'
GATEWAY_CONFIG_FILE = 'gateway_config.json'

# AWS Region - will be determined from boto3 session
AWS_REGION = None

# Initialize API Gateway client
apigateway_client = boto3.client('apigateway')


def get_aws_region() -> str:
    """
    Get the AWS region from the boto3 session.
    
    Returns:
        AWS region string
    """
    session = boto3.session.Session()
    region = session.region_name
    
    if not region:
        # Default to us-east-1 if not configured
        region = 'us-east-1'
        print(f"⚠️  WARNING: No region configured, defaulting to {region}")
    
    return region


def load_cognito_config() -> Dict:
    """
    Load Cognito configuration from file.
    
    Returns:
        Dictionary containing Cognito configuration
    """
    print("="*80)
    print("Loading Cognito Configuration")
    print("="*80)
    
    try:
        with open(COGNITO_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ Cognito configuration loaded from: {COGNITO_CONFIG_FILE}")
        print(f"   User Pool ID: {config.get('user_pool_id', 'N/A')}")
        print(f"   Domain Prefix: {config.get('domain_prefix', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: {COGNITO_CONFIG_FILE} not found")
        print("\nPlease run 08_create_cognito.py first to create Cognito configuration")
        raise
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in {COGNITO_CONFIG_FILE}: {str(e)}")
        raise


def load_gateway_role_config() -> Dict:
    """
    Load IAM role configuration from file.
    
    Returns:
        Dictionary containing IAM role configuration
    """
    print("\n" + "="*80)
    print("Loading IAM Role Configuration")
    print("="*80)
    
    try:
        with open(GATEWAY_ROLE_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ IAM role configuration loaded from: {GATEWAY_ROLE_CONFIG_FILE}")
        print(f"   Role ARN: {config.get('role_arn', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: {GATEWAY_ROLE_CONFIG_FILE} not found")
        print("\nPlease run 09_create_gateway_role.py first to create IAM role")
        raise
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in {GATEWAY_ROLE_CONFIG_FILE}: {str(e)}")
        raise


def create_rest_api() -> Dict:
    """
    Create a REST API Gateway.
    
    Returns:
        Dictionary containing API Gateway details
    """
    print("\n" + "="*80)
    print("Creating REST API Gateway")
    print("="*80)
    print(f"Gateway Name: {GATEWAY_NAME}")
    print("="*80)
    
    try:
        # Create REST API
        # NOTE: AWS API Gateway create_rest_api API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_CreateRestApi.html
        
        response = apigateway_client.create_rest_api(
            name=GATEWAY_NAME,
            description=GATEWAY_DESCRIPTION,
            endpointConfiguration={
                'types': ['REGIONAL']  # REGIONAL, EDGE, or PRIVATE
            }
        )
        
        api_id = response['id']
        api_name = response['name']
        created_date = response['createdDate']
        
        print(f"\n✅ REST API Gateway created successfully!")
        print(f"   API ID: {api_id}")
        print(f"   API Name: {api_name}")
        print(f"   Created Date: {created_date}")
        print(f"   Endpoint Type: REGIONAL")
        
        return {
            'api_id': api_id,
            'api_name': api_name,
            'created_date': str(created_date)
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create REST API: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify AWS credentials are configured")
        print("2. Check IAM permissions for apigateway:POST")
        print("3. Ensure region is correctly set")
        raise


def create_cognito_authorizer(api_id: str, user_pool_arn: str, user_pool_id: str) -> str:
    """
    Create a Cognito authorizer for the API Gateway.
    
    Args:
        api_id: The API Gateway ID
        user_pool_arn: The Cognito User Pool ARN
        user_pool_id: The Cognito User Pool ID
    
    Returns:
        Authorizer ID
    """
    print("\n" + "="*80)
    print("Creating Cognito Authorizer")
    print("="*80)
    
    try:
        # Construct User Pool ARN if not provided
        if not user_pool_arn:
            user_pool_arn = f"arn:aws:cognito-idp:{AWS_REGION}:{{account_id}}:userpool/{user_pool_id}"
            print(f"⚠️  User Pool ARN not provided, using constructed ARN")
        
        # Create Cognito authorizer
        # NOTE: AWS API Gateway create_authorizer API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_CreateAuthorizer.html
        
        response = apigateway_client.create_authorizer(
            restApiId=api_id,
            name='CognitoAuthorizer',
            type='COGNITO_USER_POOLS',
            providerARNs=[user_pool_arn],
            identitySource='method.request.header.Authorization',
            authorizerResultTtlInSeconds=300  # Cache for 5 minutes
        )
        
        authorizer_id = response['id']
        authorizer_name = response['name']
        
        print(f"\n✅ Cognito authorizer created successfully!")
        print(f"   Authorizer ID: {authorizer_id}")
        print(f"   Authorizer Name: {authorizer_name}")
        print(f"   Type: COGNITO_USER_POOLS")
        print(f"   Identity Source: Authorization header")
        
        return authorizer_id
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create Cognito authorizer: {str(e)}")
        raise


def get_api_url(api_id: str, region: str, stage: str = 'prod') -> str:
    """
    Generate the API Gateway URL.
    
    Args:
        api_id: The API Gateway ID
        region: AWS region
        stage: Deployment stage (default: prod)
    
    Returns:
        API Gateway URL
    """
    return f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"


def save_gateway_config(config: Dict) -> None:
    """
    Save API Gateway configuration to JSON file.
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("Saving Gateway Configuration")
    print("="*80)
    
    # Prepare configuration
    gateway_config = {
        'api_id': config['api_id'],
        'api_name': config['api_name'],
        'api_url': config['api_url'],
        'authorizer_id': config.get('authorizer_id'),
        'region': config['region'],
        'stage': config.get('stage', 'prod'),
        'created_at': datetime.now().isoformat()
    }
    
    with open(GATEWAY_CONFIG_FILE, 'w') as f:
        json.dump(gateway_config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {GATEWAY_CONFIG_FILE}")
    print("\nConfiguration keys:")
    for key, value in gateway_config.items():
        print(f"  • {key}: {value}")


def display_usage_instructions(config: Dict) -> None:
    """
    Display instructions for using the API Gateway.
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("USAGE INSTRUCTIONS")
    print("="*80)
    
    print("\n1. DEPLOY THE API")
    print("   Before using the API, you need to deploy it to a stage:")
    print(f"\n   aws apigateway create-deployment \\")
    print(f"     --rest-api-id {config['api_id']} \\")
    print(f"     --stage-name prod")
    
    print("\n2. CREATE API RESOURCES AND METHODS")
    print("   Add resources (endpoints) and methods (GET, POST, etc.) to your API")
    print("   Example: Create a /liability resource with POST method")
    
    print("\n3. CONFIGURE METHOD AUTHORIZATION")
    print("   Attach the Cognito authorizer to your API methods:")
    print(f"   - Authorizer ID: {config.get('authorizer_id', 'N/A')}")
    print("   - Authorization Type: COGNITO_USER_POOLS")
    
    print("\n4. TEST THE API")
    print("   Use the API URL with a valid Cognito access token:")
    print(f"\n   curl -X GET {config['api_url']}/your-resource \\")
    print("     -H 'Authorization: Bearer <access_token>'")
    
    print("\n5. INTEGRATE WITH LAMBDA")
    print("   Connect your API methods to Lambda functions:")
    print("   - Use the IAM role for Lambda invocation permissions")
    print(f"   - Role ARN: {config.get('role_arn', 'N/A')}")


def main():
    """Main execution."""
    global AWS_REGION
    
    print("\n" + "="*80)
    print("AWS API Gateway Setup")
    print("="*80)
    print(f"Gateway Name: {GATEWAY_NAME}")
    print("="*80)
    
    try:
        # Get AWS region
        AWS_REGION = get_aws_region()
        print(f"\nAWS Region: {AWS_REGION}")
        
        # Step 1: Load Cognito configuration
        print("\n" + "="*80)
        print("STEP 1: Load Cognito Configuration")
        print("="*80)
        cognito_config = load_cognito_config()
        
        # Step 2: Load IAM role configuration
        print("\n" + "="*80)
        print("STEP 2: Load IAM Role Configuration")
        print("="*80)
        role_config = load_gateway_role_config()
        
        # Step 3: Create REST API Gateway
        print("\n" + "="*80)
        print("STEP 3: Create REST API Gateway")
        print("="*80)
        api_info = create_rest_api()
        
        # Step 4: Create Cognito Authorizer
        print("\n" + "="*80)
        print("STEP 4: Create Cognito Authorizer")
        print("="*80)
        
        # Construct User Pool ARN
        user_pool_id = cognito_config['user_pool_id']
        # Note: Account ID will be retrieved from STS in production
        # For now, we'll use a placeholder that needs to be replaced
        user_pool_arn = f"arn:aws:cognito-idp:{AWS_REGION}:{{account_id}}:userpool/{user_pool_id}"
        
        authorizer_id = create_cognito_authorizer(
            api_info['api_id'],
            user_pool_arn,
            user_pool_id
        )
        
        # Step 5: Generate API URL
        print("\n" + "="*80)
        print("STEP 5: Generate API URL")
        print("="*80)
        api_url = get_api_url(api_info['api_id'], AWS_REGION)
        print(f"\n✅ API URL generated!")
        print(f"   URL: {api_url}")
        print(f"   Note: Deploy the API to activate this URL")
        
        # Step 6: Save Configuration
        print("\n" + "="*80)
        print("STEP 6: Save Configuration")
        print("="*80)
        
        config = {
            'api_id': api_info['api_id'],
            'api_name': api_info['api_name'],
            'api_url': api_url,
            'authorizer_id': authorizer_id,
            'role_arn': role_config.get('role_arn'),
            'region': AWS_REGION,
            'stage': 'prod'
        }
        
        save_gateway_config(config)
        
        # Display usage instructions
        display_usage_instructions(config)
        
        # Final summary
        print("\n" + "="*80)
        print("✅ SUCCESS: API Gateway setup completed!")
        print("="*80)
        print(f"\nAPI ID: {config['api_id']}")
        print(f"API Name: {config['api_name']}")
        print(f"API URL: {config['api_url']}")
        print(f"Authorizer ID: {config['authorizer_id']}")
        print(f"Configuration saved to: {GATEWAY_CONFIG_FILE}")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\n1. Create API resources and methods")
        print("2. Attach Cognito authorizer to methods")
        print("3. Integrate methods with Lambda functions")
        print("4. Deploy the API to a stage (e.g., prod)")
        print("5. Test the API with Cognito access token")
        
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
