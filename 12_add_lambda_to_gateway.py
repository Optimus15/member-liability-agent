#!/usr/bin/env python3
"""
Add Lambda Function to API Gateway
This script registers the OrderLookupFunction as a gateway target.

Features:
- Loads gateway configuration
- Loads Lambda function configuration
- Creates API resource (/order-lookup)
- Creates POST method with Cognito authorization
- Integrates with Lambda function
- Deploys to prod stage

Usage:
    python3 12_add_lambda_to_gateway.py
"""

import boto3
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Configuration
RESOURCE_PATH = 'order-lookup'
RESOURCE_NAME = 'OrderLookup'
HTTP_METHOD = 'POST'
GATEWAY_CONFIG_FILE = 'gateway_config.json'
LAMBDA_CONFIG_FILE = 'lambda_config.json'
INTEGRATION_CONFIG_FILE = 'lambda_integration_config.json'

# AWS Region - will be determined from boto3 session
AWS_REGION = None

# Initialize AWS clients
apigateway_client = boto3.client('apigateway')
lambda_client = boto3.client('lambda')


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


def load_gateway_config() -> Dict:
    """
    Load API Gateway configuration from file.
    
    Returns:
        Dictionary containing gateway configuration
    """
    print("="*80)
    print("Loading API Gateway Configuration")
    print("="*80)
    
    try:
        with open(GATEWAY_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ Gateway configuration loaded from: {GATEWAY_CONFIG_FILE}")
        print(f"   API ID: {config.get('api_id', 'N/A')}")
        print(f"   API Name: {config.get('api_name', 'N/A')}")
        print(f"   Authorizer ID: {config.get('authorizer_id', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: {GATEWAY_CONFIG_FILE} not found")
        print("\nPlease run 11_create_gateway.py first to create API Gateway")
        raise
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in {GATEWAY_CONFIG_FILE}: {str(e)}")
        raise


def load_lambda_config() -> Dict:
    """
    Load Lambda function configuration from file.
    
    Returns:
        Dictionary containing Lambda configuration
    """
    print("\n" + "="*80)
    print("Loading Lambda Function Configuration")
    print("="*80)
    
    try:
        with open(LAMBDA_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print(f"\n✅ Lambda configuration loaded from: {LAMBDA_CONFIG_FILE}")
        print(f"   Function Name: {config.get('function_name', 'N/A')}")
        print(f"   Function ARN: {config.get('function_arn', 'N/A')}")
        
        return config
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: {LAMBDA_CONFIG_FILE} not found")
        print("\nPlease create Lambda function and save configuration first")
        raise
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Invalid JSON in {LAMBDA_CONFIG_FILE}: {str(e)}")
        raise


def get_root_resource_id(api_id: str) -> str:
    """
    Get the root resource ID of the API Gateway.
    
    Args:
        api_id: The API Gateway ID
    
    Returns:
        Root resource ID
    """
    print("\n" + "="*80)
    print("Getting Root Resource ID")
    print("="*80)
    
    try:
        # Get all resources
        # NOTE: AWS API Gateway get_resources API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_GetResources.html
        
        response = apigateway_client.get_resources(
            restApiId=api_id
        )
        
        # Find root resource (path = '/')
        for resource in response['items']:
            if resource['path'] == '/':
                root_id = resource['id']
                print(f"\n✅ Root resource found!")
                print(f"   Resource ID: {root_id}")
                print(f"   Path: /")
                return root_id
        
        raise Exception("Root resource not found")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to get root resource: {str(e)}")
        raise


def create_api_resource(api_id: str, parent_id: str, path_part: str) -> str:
    """
    Create an API resource (endpoint).
    
    Args:
        api_id: The API Gateway ID
        parent_id: The parent resource ID
        path_part: The path part (e.g., 'order-lookup')
    
    Returns:
        Resource ID
    """
    print("\n" + "="*80)
    print("Creating API Resource")
    print("="*80)
    print(f"Path: /{path_part}")
    print("="*80)
    
    try:
        # Create resource
        # NOTE: AWS API Gateway create_resource API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_CreateResource.html
        
        response = apigateway_client.create_resource(
            restApiId=api_id,
            parentId=parent_id,
            pathPart=path_part
        )
        
        resource_id = response['id']
        resource_path = response['path']
        
        print(f"\n✅ API resource created successfully!")
        print(f"   Resource ID: {resource_id}")
        print(f"   Path: {resource_path}")
        
        return resource_id
        
    except apigateway_client.exceptions.ConflictException:
        print(f"\n⚠️  Resource /{path_part} already exists, retrieving existing resource")
        
        # Get existing resource
        response = apigateway_client.get_resources(restApiId=api_id)
        for resource in response['items']:
            if resource.get('pathPart') == path_part:
                resource_id = resource['id']
                print(f"   Resource ID: {resource_id}")
                return resource_id
        
        raise Exception(f"Resource /{path_part} exists but could not be retrieved")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create resource: {str(e)}")
        raise


def create_api_method(api_id: str, resource_id: str, http_method: str, authorizer_id: str) -> None:
    """
    Create an API method (GET, POST, etc.) with Cognito authorization.
    
    Args:
        api_id: The API Gateway ID
        resource_id: The resource ID
        http_method: The HTTP method (e.g., 'POST')
        authorizer_id: The Cognito authorizer ID
    """
    print("\n" + "="*80)
    print("Creating API Method")
    print("="*80)
    print(f"Method: {http_method}")
    print("="*80)
    
    try:
        # Create method
        # NOTE: AWS API Gateway put_method API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_PutMethod.html
        
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            authorizationType='COGNITO_USER_POOLS',
            authorizerId=authorizer_id,
            requestParameters={
                'method.request.header.Authorization': True
            }
        )
        
        print(f"\n✅ API method created successfully!")
        print(f"   Method: {http_method}")
        print(f"   Authorization: COGNITO_USER_POOLS")
        print(f"   Authorizer ID: {authorizer_id}")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create method: {str(e)}")
        raise


def create_lambda_integration(
    api_id: str,
    resource_id: str,
    http_method: str,
    lambda_arn: str,
    region: str
) -> None:
    """
    Create Lambda integration for the API method.
    
    Args:
        api_id: The API Gateway ID
        resource_id: The resource ID
        http_method: The HTTP method
        lambda_arn: The Lambda function ARN
        region: AWS region
    """
    print("\n" + "="*80)
    print("Creating Lambda Integration")
    print("="*80)
    
    try:
        # Create integration
        # NOTE: AWS API Gateway put_integration API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_PutIntegration.html
        
        # Construct Lambda URI
        lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method,
            type='AWS_PROXY',  # Lambda proxy integration
            integrationHttpMethod='POST',  # Always POST for Lambda
            uri=lambda_uri
        )
        
        print(f"\n✅ Lambda integration created successfully!")
        print(f"   Integration Type: AWS_PROXY")
        print(f"   Lambda ARN: {lambda_arn}")
        print(f"   Integration Method: POST")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create integration: {str(e)}")
        raise


def add_lambda_permission(lambda_arn: str, api_id: str, region: str, account_id: str) -> None:
    """
    Add permission for API Gateway to invoke Lambda function.
    
    Args:
        lambda_arn: The Lambda function ARN
        api_id: The API Gateway ID
        region: AWS region
        account_id: AWS account ID
    """
    print("\n" + "="*80)
    print("Adding Lambda Permission")
    print("="*80)
    
    try:
        # Extract function name from ARN
        function_name = lambda_arn.split(':')[-1]
        
        # Add permission
        # NOTE: AWS Lambda add_permission API
        # Reference: https://docs.aws.amazon.com/lambda/latest/dg/API_AddPermission.html
        
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'apigateway-{api_id}-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*/*'
        )
        
        print(f"\n✅ Lambda permission added successfully!")
        print(f"   Function: {function_name}")
        print(f"   Principal: apigateway.amazonaws.com")
        print(f"   Action: lambda:InvokeFunction")
        
    except lambda_client.exceptions.ResourceConflictException:
        print(f"\n⚠️  Permission already exists, skipping")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to add Lambda permission: {str(e)}")
        raise


def deploy_api(api_id: str, stage_name: str = 'prod') -> str:
    """
    Deploy the API to a stage.
    
    Args:
        api_id: The API Gateway ID
        stage_name: The stage name (default: prod)
    
    Returns:
        Deployment ID
    """
    print("\n" + "="*80)
    print("Deploying API")
    print("="*80)
    print(f"Stage: {stage_name}")
    print("="*80)
    
    try:
        # Create deployment
        # NOTE: AWS API Gateway create_deployment API
        # Reference: https://docs.aws.amazon.com/apigateway/latest/api/API_CreateDeployment.html
        
        response = apigateway_client.create_deployment(
            restApiId=api_id,
            stageName=stage_name,
            description=f'Deployment with {RESOURCE_NAME} Lambda integration'
        )
        
        deployment_id = response['id']
        
        print(f"\n✅ API deployed successfully!")
        print(f"   Deployment ID: {deployment_id}")
        print(f"   Stage: {stage_name}")
        
        return deployment_id
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to deploy API: {str(e)}")
        raise


def get_account_id() -> str:
    """
    Get AWS account ID using STS.
    
    Returns:
        AWS account ID
    """
    try:
        sts_client = boto3.client('sts')
        response = sts_client.get_caller_identity()
        return response['Account']
    except Exception as e:
        print(f"\n⚠️  WARNING: Could not get account ID: {str(e)}")
        return '123456789012'  # Placeholder


def save_integration_config(config: Dict) -> None:
    """
    Save Lambda integration configuration to JSON file.
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("Saving Integration Configuration")
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
        'created_at': datetime.now().isoformat()
    }
    
    with open(INTEGRATION_CONFIG_FILE, 'w') as f:
        json.dump(integration_config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {INTEGRATION_CONFIG_FILE}")
    print("\nConfiguration keys:")
    for key, value in integration_config.items():
        print(f"  • {key}: {value}")


def display_usage_instructions(config: Dict) -> None:
    """
    Display instructions for using the integrated API.
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("USAGE INSTRUCTIONS")
    print("="*80)
    
    api_url = config['api_url']
    resource_path = config['resource_path']
    
    print("\n1. GET ACCESS TOKEN")
    print("   Obtain a Cognito access token using client credentials:")
    print(f"\n   curl -X POST <cognito_token_endpoint> \\")
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
    global AWS_REGION
    
    print("\n" + "="*80)
    print("Add Lambda Function to API Gateway")
    print("="*80)
    print(f"Resource Name: {RESOURCE_NAME}")
    print(f"Resource Path: /{RESOURCE_PATH}")
    print(f"HTTP Method: {HTTP_METHOD}")
    print("="*80)
    
    try:
        # Get AWS region
        AWS_REGION = get_aws_region()
        print(f"\nAWS Region: {AWS_REGION}")
        
        # Get AWS account ID
        account_id = get_account_id()
        print(f"AWS Account ID: {account_id}")
        
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
        root_resource_id = get_root_resource_id(gateway_config['api_id'])
        
        # Step 4: Create API resource
        print("\n" + "="*80)
        print("STEP 4: Create API Resource")
        print("="*80)
        resource_id = create_api_resource(
            gateway_config['api_id'],
            root_resource_id,
            RESOURCE_PATH
        )
        
        # Step 5: Create API method
        print("\n" + "="*80)
        print("STEP 5: Create API Method")
        print("="*80)
        create_api_method(
            gateway_config['api_id'],
            resource_id,
            HTTP_METHOD,
            gateway_config['authorizer_id']
        )
        
        # Step 6: Create Lambda integration
        print("\n" + "="*80)
        print("STEP 6: Create Lambda Integration")
        print("="*80)
        create_lambda_integration(
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
        add_lambda_permission(
            lambda_config['function_arn'],
            gateway_config['api_id'],
            AWS_REGION,
            account_id
        )
        
        # Step 8: Deploy API
        print("\n" + "="*80)
        print("STEP 8: Deploy API")
        print("="*80)
        deployment_id = deploy_api(gateway_config['api_id'], 'prod')
        
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
        print("✅ SUCCESS: Lambda integration completed!")
        print("="*80)
        print(f"\nResource: /{RESOURCE_PATH}")
        print(f"Method: {HTTP_METHOD}")
        print(f"Lambda: {lambda_config['function_name']}")
        print(f"API URL: {gateway_config['api_url']}/{RESOURCE_PATH}")
        print(f"Configuration saved to: {INTEGRATION_CONFIG_FILE}")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\n1. Get Cognito access token")
        print("2. Test the API endpoint")
        print("3. Monitor Lambda function logs")
        print("4. Add additional Lambda functions as needed")
        
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
