#!/usr/bin/env python3
"""
DRY RUN VERSION - Add Lambda Function to API Gateway
This script simulates registering the OrderLookupFunction as a gateway target.

Features:
- Simulates loading gateway and Lambda configuration
- Simulates creating API resource
- Simulates creating POST method with Cognito authorization
- Simulates Lambda integration
- Saves configuration to lambda_integration_config_dryrun.json

Usage:
    python3 12_add_lambda_to_gateway_dryrun.py
"""

import json
import sys
from datetime import datetime
from typing import Dict
import time

# Configuration
RESOURCE_PATH = 'order-lookup'
RESOURCE_NAME = 'OrderLookup'
HTTP_METHOD = 'POST'
GATEWAY_CONFIG_FILE = 'gateway_config_dryrun.json'
LAMBDA_CONFIG_FILE = 'lambda_config_dryrun.json'
INTEGRATION_CONFIG_FILE = 'lambda_integration_config_dryrun.json'
AWS_REGION = 'us-east-1'
AWS_ACCOUNT_ID = '123456789012'


def load_gateway_config() -> Dict:
    """Load API Gateway configuration from file."""
    print("="*80)
    print("Loading API Gateway Configuration (DRY RUN)")
    print("="*80)
    
    try:
        with open(GATEWAY_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ [DRY RUN] Gateway configuration loaded from: {GATEWAY_CONFIG_FILE}")
        print(f"   API ID: {config.get('api_id', 'N/A')}")
        print(f"   API Name: {config.get('api_name', 'N/A')}")
        print(f"   Authorizer ID: {config.get('authorizer_id', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: {GATEWAY_CONFIG_FILE} not found")
        print("\nPlease run 11_create_gateway_dryrun.py first")
        raise


def load_lambda_config() -> Dict:
    """Load Lambda function configuration from file."""
    print("\n" + "="*80)
    print("Loading Lambda Function Configuration (DRY RUN)")
    print("="*80)
    
    try:
        with open(LAMBDA_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ [DRY RUN] Lambda configuration loaded from: {LAMBDA_CONFIG_FILE}")
        print(f"   Function Name: {config.get('function_name', 'N/A')}")
        print(f"   Function ARN: {config.get('function_arn', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n⚠️  WARNING: {LAMBDA_CONFIG_FILE} not found")
        print("   Creating placeholder configuration for dry run")
        
        # Create placeholder config
        placeholder_config = {
            'function_name': 'OrderLookupFunction',
            'function_arn': f'arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:OrderLookupFunction',
            'created_at': datetime.now().isoformat(),
            'dry_run': True
        }
        
        with open(LAMBDA_CONFIG_FILE, 'w') as f:
            json.dump(placeholder_config, f, indent=2)
        
        print(f"   Created: {LAMBDA_CONFIG_FILE}")
        return placeholder_config


def simulate_get_root_resource_id(api_id: str) -> str:
    """Simulate getting the root resource ID."""
    print("\n" + "="*80)
    print("Getting Root Resource ID (DRY RUN)")
    print("="*80)
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.get_resources()")
    print(f"   restApiId: {api_id}")
    
    root_id = f"root{int(time.time())}"
    
    print(f"\n✅ [DRY RUN] Root resource would be found!")
    print(f"   Resource ID: {root_id}")
    print(f"   Path: /")
    
    return root_id


def simulate_create_api_resource(api_id: str, parent_id: str, path_part: str) -> str:
    """Simulate creating an API resource."""
    print("\n" + "="*80)
    print("Creating API Resource (DRY RUN)")
    print("="*80)
    print(f"Path: /{path_part}")
    print("="*80)
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.create_resource()")
    print(f"   restApiId: {api_id}")
    print(f"   parentId: {parent_id}")
    print(f"   pathPart: {path_part}")
    
    resource_id = f"res{int(time.time())}"
    
    print(f"\n✅ [DRY RUN] API resource would be created successfully!")
    print(f"   Resource ID: {resource_id}")
    print(f"   Path: /{path_part}")
    
    return resource_id


def simulate_create_api_method(api_id: str, resource_id: str, http_method: str, authorizer_id: str) -> None:
    """Simulate creating an API method."""
    print("\n" + "="*80)
    print("Creating API Method (DRY RUN)")
    print("="*80)
    print(f"Method: {http_method}")
    print("="*80)
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.put_method()")
    print(f"   restApiId: {api_id}")
    print(f"   resourceId: {resource_id}")
    print(f"   httpMethod: {http_method}")
    print("   authorizationType: COGNITO_USER_POOLS")
    print(f"   authorizerId: {authorizer_id}")
    print("   requestParameters:")
    print("     method.request.header.Authorization: True")
    
    print(f"\n✅ [DRY RUN] API method would be created successfully!")
    print(f"   Method: {http_method}")
    print("   Authorization: COGNITO_USER_POOLS")
    print(f"   Authorizer ID: {authorizer_id}")


def simulate_create_lambda_integration(
    api_id: str,
    resource_id: str,
    http_method: str,
    lambda_arn: str,
    region: str
) -> None:
    """Simulate creating Lambda integration."""
    print("\n" + "="*80)
    print("Creating Lambda Integration (DRY RUN)")
    print("="*80)
    
    lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.put_integration()")
    print(f"   restApiId: {api_id}")
    print(f"   resourceId: {resource_id}")
    print(f"   httpMethod: {http_method}")
    print("   type: AWS_PROXY")
    print("   integrationHttpMethod: POST")
    print(f"   uri: {lambda_uri}")
    
    print(f"\n✅ [DRY RUN] Lambda integration would be created successfully!")
    print("   Integration Type: AWS_PROXY")
    print(f"   Lambda ARN: {lambda_arn}")
    print("   Integration Method: POST")


def simulate_add_lambda_permission(lambda_arn: str, api_id: str, region: str, account_id: str) -> None:
    """Simulate adding Lambda permission."""
    print("\n" + "="*80)
    print("Adding Lambda Permission (DRY RUN)")
    print("="*80)
    
    function_name = lambda_arn.split(':')[-1]
    
    print("\n🔄 [DRY RUN] Would call: lambda_client.add_permission()")
    print(f"   FunctionName: {function_name}")
    print(f"   StatementId: apigateway-{api_id}-invoke")
    print("   Action: lambda:InvokeFunction")
    print("   Principal: apigateway.amazonaws.com")
    print(f"   SourceArn: arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*/*")
    
    print(f"\n✅ [DRY RUN] Lambda permission would be added successfully!")
    print(f"   Function: {function_name}")
    print("   Principal: apigateway.amazonaws.com")
    print("   Action: lambda:InvokeFunction")


def simulate_deploy_api(api_id: str, stage_name: str = 'prod') -> str:
    """Simulate deploying the API."""
    print("\n" + "="*80)
    print("Deploying API (DRY RUN)")
    print("="*80)
    print(f"Stage: {stage_name}")
    print("="*80)
    
    print("\n🔄 [DRY RUN] Would call: apigateway_client.create_deployment()")
    print(f"   restApiId: {api_id}")
    print(f"   stageName: {stage_name}")
    print(f"   description: Deployment with {RESOURCE_NAME} Lambda integration")
    
    deployment_id = f"deploy{int(time.time())}"
    
    print(f"\n✅ [DRY RUN] API would be deployed successfully!")
    print(f"   Deployment ID: {deployment_id}")
    print(f"   Stage: {stage_name}")
    
    return deployment_id


def save_integration_config(config: Dict) -> None:
    """Save Lambda integration configuration to JSON file."""
    print("\n" + "="*80)
    print("Saving Integration Configuration (DRY RUN)")
    print("="*80)
    
    integration_config = {
        'resource_name': config['resource_name'],
        'resource_path': config['resource_path'],
        'resource_id': config['resource_id'],
        'http_method': config['http_method'],
        'lambda_function': config['lambda_function'],
        'lambda_arn': config['lambda_arn'],
        'api_id': config['api_id'],
        'deployment_id': config.get('deployment_id'),
        'stage': config.get('stage', 'prod'),
        'created_at': datetime.now().isoformat(),
        'dry_run': True
    }
    
    with open(INTEGRATION_CONFIG_FILE, 'w') as f:
        json.dump(integration_config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {INTEGRATION_CONFIG_FILE}")
    print("\nConfiguration keys:")
    for key, value in integration_config.items():
        print(f"  • {key}: {value}")


def display_usage_instructions(config: Dict) -> None:
    """Display instructions for using the integrated API."""
    print("\n" + "="*80)
    print("USAGE INSTRUCTIONS")
    print("="*80)
    
    api_url = config['api_url']
    resource_path = config['resource_path']
    
    print("\n1. GET ACCESS TOKEN")
    print("   Obtain a Cognito access token using client credentials:")
    print("\n   curl -X POST <cognito_token_endpoint> \\")
    print("     -H 'Content-Type: application/x-www-form-urlencoded' \\")
    print("     -d 'grant_type=client_credentials' \\")
    print("     -d 'client_id=<client_id>' \\")
    print("     -d 'client_secret=<client_secret>' \\")
    print("     -d 'scope=member-liability-api/read member-liability-api/write'")
    
    print("\n2. CALL THE API")
    print(f"   Use the access token to call the {RESOURCE_NAME} endpoint:")
    print(f"\n   curl -X POST {api_url}/{resource_path} \\")
    print("     -H 'Authorization: Bearer <access_token>' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"order_id\": \"12345\"}'")
    
    print("\n3. EXPECTED RESPONSE")
    print("   The Lambda function will process the request and return:")
    print("   - Order details")
    print("   - Status code: 200")
    print("   - JSON response body")


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("Add Lambda Function to API Gateway (DRY RUN)")
    print("="*80)
    print(f"Resource Name: {RESOURCE_NAME}")
    print(f"Resource Path: /{RESOURCE_PATH}")
    print(f"HTTP Method: {HTTP_METHOD}")
    print("="*80)
    print("\n⚠️  DRY RUN MODE: No actual AWS API calls will be made")
    print("   This simulates the Lambda integration process\n")
    
    try:
        print(f"\nAWS Region: {AWS_REGION}")
        print(f"AWS Account ID: {AWS_ACCOUNT_ID}")
        
        # Step 1: Load Gateway configuration
        print("\n" + "="*80)
        print("STEP 1: Load Gateway Configuration")
        print("="*80)
        gateway_config = load_gateway_config()
        
        # Step 2: Load Lambda configuration
        print("\n" + "="*80)
        print("STEP 2: Load Lambda Configuration")
        print("="*80)
        lambda_config = load_lambda_config()
        
        # Step 3: Get root resource ID
        print("\n" + "="*80)
        print("STEP 3: Get Root Resource ID")
        print("="*80)
        root_resource_id = simulate_get_root_resource_id(gateway_config['api_id'])
        
        # Step 4: Create API resource
        print("\n" + "="*80)
        print("STEP 4: Create API Resource")
        print("="*80)
        resource_id = simulate_create_api_resource(
            gateway_config['api_id'],
            root_resource_id,
            RESOURCE_PATH
        )
        
        # Step 5: Create API method
        print("\n" + "="*80)
        print("STEP 5: Create API Method")
        print("="*80)
        simulate_create_api_method(
            gateway_config['api_id'],
            resource_id,
            HTTP_METHOD,
            gateway_config['authorizer_id']
        )
        
        # Step 6: Create Lambda integration
        print("\n" + "="*80)
        print("STEP 6: Create Lambda Integration")
        print("="*80)
        simulate_create_lambda_integration(
            gateway_config['api_id'],
            resource_id,
            HTTP_METHOD,
            lambda_config['function_arn'],
            AWS_REGION
        )
        
        # Step 7: Add Lambda permission
        print("\n" + "="*80)
        print("STEP 7: Add Lambda Permission")
        print("="*80)
        simulate_add_lambda_permission(
            lambda_config['function_arn'],
            gateway_config['api_id'],
            AWS_REGION,
            AWS_ACCOUNT_ID
        )
        
        # Step 8: Deploy API
        print("\n" + "="*80)
        print("STEP 8: Deploy API")
        print("="*80)
        deployment_id = simulate_deploy_api(gateway_config['api_id'], 'prod')
        
        # Step 9: Save configuration
        print("\n" + "="*80)
        print("STEP 9: Save Configuration")
        print("="*80)
        
        config = {
            'resource_name': RESOURCE_NAME,
            'resource_path': RESOURCE_PATH,
            'resource_id': resource_id,
            'http_method': HTTP_METHOD,
            'lambda_function': lambda_config['function_name'],
            'lambda_arn': lambda_config['function_arn'],
            'api_id': gateway_config['api_id'],
            'api_url': gateway_config['api_url'],
            'deployment_id': deployment_id,
            'stage': 'prod'
        }
        
        save_integration_config(config)
        
        # Display usage instructions
        display_usage_instructions(config)
        
        # Final summary
        print("\n" + "="*80)
        print("✅ SUCCESS: Lambda integration simulation completed!")
        print("="*80)
        print(f"\nResource: /{RESOURCE_PATH}")
        print(f"Method: {HTTP_METHOD}")
        print(f"Lambda: {lambda_config['function_name']}")
        print(f"API URL: {gateway_config['api_url']}/{RESOURCE_PATH}")
        print(f"Configuration saved to: {INTEGRATION_CONFIG_FILE}")
        
        print("\n" + "="*80)
        print("PRODUCTION DEPLOYMENT")
        print("="*80)
        print("\nTo run this in production:")
        print("\n1. Configure AWS credentials:")
        print("   aws configure")
        print("\n2. Create Lambda function (OrderLookupFunction)")
        print("\n3. Run the production script:")
        print("   python3 12_add_lambda_to_gateway.py")
        print("\n4. Test the API endpoint")
        print("\n5. Monitor Lambda function logs")
        
        print("\n" + "="*80)
        print("WHAT WAS CREATED (SIMULATED)")
        print("="*80)
        print(f"\n✅ API Resource: /{RESOURCE_PATH}")
        print(f"✅ API Method: {HTTP_METHOD} with Cognito authorization")
        print("✅ Lambda integration (AWS_PROXY)")
        print("✅ Lambda invocation permission")
        print("✅ API deployment to prod stage")
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
