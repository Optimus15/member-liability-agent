#!/usr/bin/env python3
"""
Create AWS Cognito Authentication for Gateway
This script sets up a Cognito User Pool with OAuth support for machine-to-machine
authentication, enabling secure gateway access for the Bedrock Agent.

Features:
- Creates Cognito User Pool (secure login system)
- Adds domain prefix for OAuth endpoints
- Configures OAuth with read/write permissions
- Creates app client for machine-to-machine authentication
- Saves credentials to cognito_config.json

Usage:
    python3 08_create_cognito.py
"""

import boto3
import json
import sys
from datetime import datetime
from typing import Dict, Optional

# Configuration
USER_POOL_NAME = 'member-liability-gateway-pool'
DOMAIN_PREFIX = 'member-liability-gateway'  # Must be globally unique
APP_CLIENT_NAME = 'member-liability-agent-client'
CONFIG_FILE = 'cognito_config.json'

# AWS Region - will be determined from boto3 session
AWS_REGION = None

# Initialize Cognito client
cognito_client = boto3.client('cognito-idp')


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


def create_user_pool() -> Dict:
    """
    Create a Cognito User Pool for authentication.
    
    A User Pool is like a secure login system that manages user authentication.
    
    Returns:
        Dictionary containing user pool details
    """
    print("="*80)
    print("Creating Cognito User Pool")
    print("="*80)
    print(f"Pool Name: {USER_POOL_NAME}")
    print("="*80)
    
    try:
        # Create user pool with OAuth configuration
        # NOTE: AWS Cognito User Pool API
        # Reference: https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateUserPool.html
        
        response = cognito_client.create_user_pool(
            PoolName=USER_POOL_NAME,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': False
                }
            },
            AutoVerifiedAttributes=['email'],
            Schema=[
                {
                    'Name': 'email',
                    'AttributeDataType': 'String',
                    'Required': True,
                    'Mutable': True
                }
            ],
            # Enable OAuth flows for machine-to-machine authentication
            UserPoolAddOns={
                'AdvancedSecurityMode': 'OFF'  # Can be enabled for production
            }
        )
        
        user_pool_id = response['UserPool']['Id']
        user_pool_arn = response['UserPool']['Arn']
        
        print(f"\n✅ User Pool created successfully!")
        print(f"   User Pool ID: {user_pool_id}")
        print(f"   User Pool ARN: {user_pool_arn}")
        
        return {
            'user_pool_id': user_pool_id,
            'user_pool_arn': user_pool_arn
        }
        
    except cognito_client.exceptions.UserPoolTaggingException as e:
        print(f"\n❌ ERROR: Failed to create user pool: {str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create user pool: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify AWS credentials are configured")
        print("2. Check IAM permissions for cognito-idp:CreateUserPool")
        print("3. Ensure region is correctly set")
        raise


def create_user_pool_domain(user_pool_id: str, domain_prefix: str) -> str:
    """
    Create a domain prefix for OAuth endpoints.
    
    This is required for token generation and OAuth flows.
    
    Args:
        user_pool_id: The Cognito User Pool ID
        domain_prefix: The domain prefix (must be globally unique)
    
    Returns:
        The domain prefix
    """
    print("\n" + "="*80)
    print("Creating User Pool Domain")
    print("="*80)
    print(f"Domain Prefix: {domain_prefix}")
    print("="*80)
    
    try:
        # Create user pool domain
        # NOTE: The domain prefix must be globally unique across all AWS accounts
        cognito_client.create_user_pool_domain(
            Domain=domain_prefix,
            UserPoolId=user_pool_id
        )
        
        print(f"\n✅ Domain created successfully!")
        print(f"   Domain Prefix: {domain_prefix}")
        print(f"   Full Domain: {domain_prefix}.auth.{AWS_REGION}.amazoncognito.com")
        
        return domain_prefix
        
    except cognito_client.exceptions.InvalidParameterException as e:
        print(f"\n❌ ERROR: Invalid domain prefix: {str(e)}")
        print("\nNote: Domain prefix must be globally unique.")
        print("Try adding a timestamp or random string to make it unique.")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create domain: {str(e)}")
        raise


def create_resource_server(user_pool_id: str) -> str:
    """
    Create a resource server with custom scopes for OAuth.
    
    This defines the read/write permissions for the API.
    
    Args:
        user_pool_id: The Cognito User Pool ID
    
    Returns:
        Resource server identifier
    """
    print("\n" + "="*80)
    print("Creating Resource Server")
    print("="*80)
    
    resource_server_identifier = 'member-liability-api'
    
    try:
        # Create resource server with custom scopes
        cognito_client.create_resource_server(
            UserPoolId=user_pool_id,
            Identifier=resource_server_identifier,
            Name='Member Liability API',
            Scopes=[
                {
                    'ScopeName': 'read',
                    'ScopeDescription': 'Read access to member liability data'
                },
                {
                    'ScopeName': 'write',
                    'ScopeDescription': 'Write access to member liability data'
                }
            ]
        )
        
        print(f"\n✅ Resource server created successfully!")
        print(f"   Identifier: {resource_server_identifier}")
        print(f"   Scopes: {resource_server_identifier}/read, {resource_server_identifier}/write")
        
        return resource_server_identifier
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create resource server: {str(e)}")
        raise


def create_app_client(user_pool_id: str, resource_server_identifier: str) -> Dict:
    """
    Create an app client for machine-to-machine authentication.
    
    This allows the Bedrock Agent to securely authenticate with the gateway.
    
    Args:
        user_pool_id: The Cognito User Pool ID
        resource_server_identifier: The resource server identifier
    
    Returns:
        Dictionary containing app client details
    """
    print("\n" + "="*80)
    print("Creating App Client")
    print("="*80)
    print(f"Client Name: {APP_CLIENT_NAME}")
    print("="*80)
    
    try:
        # Create app client with OAuth client credentials flow
        # NOTE: This is for machine-to-machine authentication
        response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=APP_CLIENT_NAME,
            GenerateSecret=True,  # Required for client credentials flow
            # OAuth configuration
            AllowedOAuthFlows=['client_credentials'],
            AllowedOAuthScopes=[
                f'{resource_server_identifier}/read',
                f'{resource_server_identifier}/write'
            ],
            AllowedOAuthFlowsUserPoolClient=True,
            # Token validity
            AccessTokenValidity=60,  # 60 minutes
            TokenValidityUnits={
                'AccessToken': 'minutes'
            }
        )
        
        client_id = response['UserPoolClient']['ClientId']
        client_secret = response['UserPoolClient']['ClientSecret']
        
        print(f"\n✅ App client created successfully!")
        print(f"   Client ID: {client_id}")
        print(f"   Client Secret: {client_secret[:10]}... (hidden)")
        print(f"   OAuth Flows: client_credentials")
        print(f"   Scopes: read, write")
        
        return {
            'client_id': client_id,
            'client_secret': client_secret
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create app client: {str(e)}")
        raise


def generate_oauth_urls(domain_prefix: str, region: str) -> Dict:
    """
    Generate OAuth endpoint URLs.
    
    Args:
        domain_prefix: The domain prefix
        region: AWS region
    
    Returns:
        Dictionary containing OAuth URLs
    """
    print("\n" + "="*80)
    print("Generating OAuth URLs")
    print("="*80)
    
    # Construct OAuth URLs
    base_url = f"https://{domain_prefix}.auth.{region}.amazoncognito.com"
    token_endpoint = f"{base_url}/oauth2/token"
    discovery_url = f"{base_url}/.well-known/openid-configuration"
    
    print(f"\n✅ OAuth URLs generated!")
    print(f"   Token Endpoint: {token_endpoint}")
    print(f"   Discovery URL: {discovery_url}")
    
    return {
        'token_endpoint': token_endpoint,
        'discovery_url': discovery_url
    }


def save_cognito_config(config: Dict) -> None:
    """
    Save Cognito configuration to JSON file.
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("Saving Configuration")
    print("="*80)
    
    # Prepare configuration with exact keys as specified
    cognito_config = {
        'user_pool_id': config['user_pool_id'],
        'domain_prefix': config['domain_prefix'],  # NOT "domain"
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'token_endpoint': config['token_endpoint'],
        'discovery_url': config['discovery_url'],
        'created_at': datetime.now().isoformat(),
        'region': config['region']
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cognito_config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {CONFIG_FILE}")
    print("\nConfiguration keys:")
    for key in cognito_config.keys():
        if key == 'client_secret':
            print(f"  • {key}: {cognito_config[key][:10]}... (hidden)")
        elif key in ['created_at', 'region']:
            print(f"  • {key}: {cognito_config[key]}")
        else:
            print(f"  • {key}: {cognito_config[key]}")


def display_usage_instructions(config: Dict) -> None:
    """
    Display instructions for using the Cognito configuration.
    
    Args:
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("USAGE INSTRUCTIONS")
    print("="*80)
    
    print("\n1. OBTAIN ACCESS TOKEN")
    print("   Use the client credentials flow to get an access token:")
    print(f"\n   curl -X POST {config['token_endpoint']} \\")
    print(f"     -H 'Content-Type: application/x-www-form-urlencoded' \\")
    print(f"     -d 'grant_type=client_credentials' \\")
    print(f"     -d 'client_id={config['client_id']}' \\")
    print(f"     -d 'client_secret={config['client_secret'][:10]}...' \\")
    print(f"     -d 'scope=member-liability-api/read member-liability-api/write'")
    
    print("\n2. USE ACCESS TOKEN")
    print("   Include the access token in API requests:")
    print("\n   curl -X GET https://your-api-gateway.com/endpoint \\")
    print("     -H 'Authorization: Bearer <access_token>'")
    
    print("\n3. CONFIGURE API GATEWAY")
    print("   In API Gateway, add a Cognito authorizer:")
    print(f"   - User Pool: {config['user_pool_id']}")
    print(f"   - Token Source: Authorization header")
    print(f"   - Token Validation: Automatic")
    
    print("\n4. PYTHON EXAMPLE")
    print("   ```python")
    print("   import requests")
    print("   import base64")
    print()
    print("   # Get access token")
    print(f"   token_url = '{config['token_endpoint']}'")
    print(f"   client_id = '{config['client_id']}'")
    print(f"   client_secret = '{config['client_secret'][:10]}...'")
    print()
    print("   # Encode credentials")
    print("   credentials = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()")
    print()
    print("   # Request token")
    print("   response = requests.post(token_url,")
    print("       headers={'Authorization': f'Basic {credentials}'},")
    print("       data={'grant_type': 'client_credentials',")
    print("             'scope': 'member-liability-api/read member-liability-api/write'}")
    print("   )")
    print("   access_token = response.json()['access_token']")
    print()
    print("   # Use token in API calls")
    print("   api_response = requests.get('https://your-api.com/endpoint',")
    print("       headers={'Authorization': f'Bearer {access_token}'}")
    print("   )")
    print("   ```")


def main():
    """Main execution."""
    global AWS_REGION
    
    print("\n" + "="*80)
    print("AWS Cognito Authentication Setup")
    print("="*80)
    print(f"User Pool Name: {USER_POOL_NAME}")
    print(f"Domain Prefix: {DOMAIN_PREFIX}")
    print(f"App Client Name: {APP_CLIENT_NAME}")
    print("="*80)
    
    try:
        # Get AWS region
        AWS_REGION = get_aws_region()
        print(f"\nAWS Region: {AWS_REGION}")
        
        # Step 1: Create User Pool
        print("\n" + "="*80)
        print("STEP 1: Create User Pool")
        print("="*80)
        user_pool = create_user_pool()
        
        # Step 2: Create Domain
        print("\n" + "="*80)
        print("STEP 2: Create Domain Prefix")
        print("="*80)
        domain_prefix = create_user_pool_domain(
            user_pool['user_pool_id'],
            DOMAIN_PREFIX
        )
        
        # Step 3: Create Resource Server
        print("\n" + "="*80)
        print("STEP 3: Create Resource Server with OAuth Scopes")
        print("="*80)
        resource_server_id = create_resource_server(user_pool['user_pool_id'])
        
        # Step 4: Create App Client
        print("\n" + "="*80)
        print("STEP 4: Create App Client for Machine-to-Machine Auth")
        print("="*80)
        app_client = create_app_client(
            user_pool['user_pool_id'],
            resource_server_id
        )
        
        # Step 5: Generate OAuth URLs
        print("\n" + "="*80)
        print("STEP 5: Generate OAuth URLs")
        print("="*80)
        oauth_urls = generate_oauth_urls(domain_prefix, AWS_REGION)
        
        # Step 6: Save Configuration
        print("\n" + "="*80)
        print("STEP 6: Save Configuration")
        print("="*80)
        
        config = {
            'user_pool_id': user_pool['user_pool_id'],
            'domain_prefix': domain_prefix,
            'client_id': app_client['client_id'],
            'client_secret': app_client['client_secret'],
            'token_endpoint': oauth_urls['token_endpoint'],
            'discovery_url': oauth_urls['discovery_url'],
            'region': AWS_REGION
        }
        
        save_cognito_config(config)
        
        # Display usage instructions
        display_usage_instructions(config)
        
        # Final summary
        print("\n" + "="*80)
        print("✅ SUCCESS: Cognito authentication setup completed!")
        print("="*80)
        print(f"\nUser Pool ID: {config['user_pool_id']}")
        print(f"Domain Prefix: {config['domain_prefix']}")
        print(f"Client ID: {config['client_id']}")
        print(f"Configuration saved to: {CONFIG_FILE}")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\n1. Configure API Gateway with Cognito authorizer")
        print("2. Test token generation using the curl command above")
        print("3. Update Bedrock Agent to use the access token")
        print("4. Test end-to-end authentication flow")
        
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
