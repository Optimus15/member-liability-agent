#!/usr/bin/env python3
"""
DRY RUN VERSION - Create AWS API Gateway for Member Liability Agent
This script simulates creating a REST API Gateway without AWS credentials.

Features:
- Simulates REST API Gateway creation
- Loads Cognito and IAM role configuration
- Simulates Cognito authorizer creation
- Saves gateway ID and URL to gateway_config_dryrun.json

Usage:
    python3 11_create_gateway_dryrun.py
"""

import json
import sys
from datetime import datetime
from typing import Dict
import time

# Configuration
GATEWAY_NAME = 'ReturnsRefundsGateway'
GATEWAY_DESCRIPTION = 'API Gateway for Member Liability Agent with Cognito authentication'
COGNITO_CONFIG_FILE = 'cognito_config_dryrun.json'
GATEWAY_ROLE_CONFIG_FILE = 'gateway_role_config_dryrun.json'
GATEWAY_CONFIG_FILE = 'gateway_config_dryrun.json'
AWS_REGION = 'us-east-1'


def load_cognito_config() -> Dict:
    """Load Cognito configuration from file."""
    print("="*80)
    print("Loading Cognito Configuration (DRY RUN)")
    print("="*80)
    
    try:
        with open(COGNITO_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ [DRY RUN] Cognito configuration loaded from: {COGNITO_CONFIG_FILE}")
        print(f"   User Pool ID: {config.get('user_pool_id', 'N/A')}")
        print(f"   Domain Prefix: {config.get('domain_prefix', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: {COGNITO_CONFIG_FILE} not found")
        print("\nPlease run 08_create_cognito_dryrun.py first")
        raise
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in {COGNITO_CONFIG_FILE}: {str(e)}")
        raise


def load_gateway_role_config() -> Dict:
    """Load IAM role configuration from file."""
    print("\n" + "="*80)
    print("Loading IAM Role Configuration (DRY RUN)")
    print("="*80)
    
    try:
        with open(GATEWAY_ROLE_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ [DRY RUN] IAM role configuration loaded from: {GATEWAY_ROLE_CONFIG_FILE}")
        print(f"   Role ARN: {config.get('role_arn', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n⚠️  WARNING: {GATEWAY_ROLE_CONFIG_FILE} not found")
        print("   Creating placeholder configuration for dry run")
        
        # Create placeholder config for dry run
        placeholder_config = {
            'role_arn': f'arn:aws:iam::123456789012:role/GatewayLambdaInvokeRole',
            'role_name': 'GatewayLambdaInvokeRole',
            'created_at': datetime.now().isoformat(),
            'dry_run': True
        }
        
        with open(GATEWAY_ROLE_CONFIG_FILE, 'w') as f:
            json.dump(placeholder_config, f, indent=2)
        
        print(f"   Created: {GATEWAY_ROLE_CONFIG_FILE}")
        return placeholder_config
        
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in {GATEWAY_ROLE_CONFIG_FILE}: {str(e)}")
        raise


def simulate_create_rest_api() -> Dict:
    """Simulate creating a REST API Gateway."""
    print("\n" + "="*80)
    print("Creating REST API Gateway (DRY RUN)")
    print("="*80)
    print(f"Gateway Name: {GATEWAY_NAME}")
    print("="*80)
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.create_rest_api()")
    print(f"   name: {GATEWAY_NAME}")
    print(f"   description: {GATEWAY_DESCRIPTION}")
    print("   endpointConfiguration:")
    print("     types: ['REGIONAL']")
    
    # Simulate response
    api_id = f"dryrun{int(time.time())}"
    created_date = datetime.now().isoformat()
    
    print(f"\n✅ [DRY RUN] REST API Gateway would be created successfully!")
    print(f"   API ID: {api_id}")
    print(f"   API Name: {GATEWAY_NAME}")
    print(f"   Created Date: {created_date}")
    print(f"   Endpoint Type: REGIONAL")
    
    return {
        'api_id': api_id,
        'api_name': GATEWAY_NAME,
        'created_date': created_date
    }


def simulate_create_cognito_authorizer(api_id: str, user_pool_arn: str, user_pool_id: str) -> str:
    """Simulate creating a Cognito authorizer."""
    print("\n" + "="*80)
    print("Creating Cognito Authorizer (DRY RUN)")
    print("="*80)
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.create_authorizer()")
    print(f"   restApiId: {api_id}")
    print("   name: CognitoAuthorizer")
    print("   type: COGNITO_USER_POOLS")
    print(f"   providerARNs: [{user_pool_arn}]")
    print("   identitySource: method.request.header.Authorization")
    print("   authorizerResultTtlInSeconds: 300")
    
    # Simulate response
    authorizer_id = f"auth{int(time.time())}"
    
    print(f"\n✅ [DRY RUN] Cognito authorizer would be created successfully!")
    print(f"   Authorizer ID: {authorizer_id}")
    print("   Authorizer Name: CognitoAuthorizer")
    print("   Type: COGNITO_USER_POOLS")
    print("   Identity Source: Authorization header")
    
    return authorizer_id


def get_api_url(api_id: str, region: str, stage: str = 'prod') -> str:
    """Generate the API Gateway URL."""
    return f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"


def save_gateway_config(config: Dict) -> None:
    """Save API Gateway configuration to JSON file."""
    print("\n" + "="*80)
    print("Saving Gateway Configuration (DRY RUN)")
    print("="*80)
    
    # Prepare configuration
    gateway_config = {
        'api_id': config['api_id'],
        'api_name': config['api_name'],
        'api_url': config['api_url'],
        'authorizer_id': config.get('authorizer_id'),
        'region': config['region'],
        'stage': config.get('stage', 'prod'),
        'created_at': datetime.now().isoformat(),
        'dry_run': True
    }
    
    with open(GATEWAY_CONFIG_FILE, 'w') as f:
        json.dump(gateway_config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {GATEWAY_CONFIG_FILE}")
    print("\nConfiguration keys:")
    for key, value in gateway_config.items():
        print(f"  • {key}: {value}")


def display_usage_instructions(config: Dict) -> None:
    """Display instructions for using the API Gateway."""
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
    print("\n" + "="*80)
    print("AWS API Gateway Setup (DRY RUN)")
    print("="*80)
    print(f"Gateway Name: {GATEWAY_NAME}")
    print("="*80)
    print("\n⚠️  DRY RUN MODE: No actual AWS API calls will be made")
    print("   This simulates the API Gateway setup process\n")
    
    try:
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
        api_info = simulate_create_rest_api()
        
        # Step 4: Create Cognito Authorizer
        print("\n" + "="*80)
        print("STEP 4: Create Cognito Authorizer")
        print("="*80)
        
        # Construct User Pool ARN
        user_pool_id = cognito_config['user_pool_id']
        user_pool_arn = f"arn:aws:cognito-idp:{AWS_REGION}:123456789012:userpool/{user_pool_id}"
        
        authorizer_id = simulate_create_cognito_authorizer(
            api_info['api_id'],
            user_pool_arn,
            user_pool_id
        )
        
        # Step 5: Generate API URL
        print("\n" + "="*80)
        print("STEP 5: Generate API URL")
        print("="*80)
        api_url = get_api_url(api_info['api_id'], AWS_REGION)
        print(f"\n✅ [DRY RUN] API URL would be generated!")
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
        print("✅ SUCCESS: API Gateway setup simulation completed!")
        print("="*80)
        print(f"\nAPI ID: {config['api_id']}")
        print(f"API Name: {config['api_name']}")
        print(f"API URL: {config['api_url']}")
        print(f"Authorizer ID: {config['authorizer_id']}")
        print(f"Configuration saved to: {GATEWAY_CONFIG_FILE}")
        
        print("\n" + "="*80)
        print("PRODUCTION DEPLOYMENT")
        print("="*80)
        print("\nTo run this in production:")
        print("\n1. Configure AWS credentials:")
        print("   aws configure")
        print("\n2. Run the production script:")
        print("   python3 11_create_gateway.py")
        print("\n3. Create API resources and methods")
        print("\n4. Deploy the API to a stage")
        print("\n5. Test with Cognito access token")
        
        print("\n" + "="*80)
        print("WHAT WAS CREATED (SIMULATED)")
        print("="*80)
        print("\n✅ REST API Gateway (ReturnsRefundsGateway)")
        print("✅ Cognito authorizer for authentication")
        print("✅ API URL for accessing the gateway")
        print("✅ Configuration file with all details")
        
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
