#!/usr/bin/env python3
"""
Member Benefits & Liability MCP Server
This MCP server provides tools for AI assistants to access member eligibility,
benefits, and liability APIs through the API Gateway.

Features:
- Member Eligibility API integration
- Member Benefits API integration
- Member Liability API integration
- API Gateway authentication (Cognito)
- Secure token management

Usage:
    python3 16_member_benefits_liability_mcpserver.py

MCP Configuration (add to mcp.json):
{
  "mcpServers": {
    "member-benefits-liability": {
      "command": "python3",
      "args": ["01_member_liability_agent/16_member_benefits_liability_mcpserver.py"],
      "env": {
        "GATEWAY_API_URL": "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod",
        "COGNITO_TOKEN_ENDPOINT": "https://your-domain.auth.us-east-1.amazoncognito.com/oauth2/token",
        "COGNITO_CLIENT_ID": "your-client-id",
        "COGNITO_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional
import base64
import time

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# HTTP client
try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Install with: pip install httpx", file=sys.stderr)
    sys.exit(1)


# Configuration from environment variables
GATEWAY_API_URL = os.getenv('GATEWAY_API_URL', '')
COGNITO_TOKEN_ENDPOINT = os.getenv('COGNITO_TOKEN_ENDPOINT', '')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID', '')
COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET', '')

# Token cache
_token_cache = {
    'access_token': None,
    'expires_at': 0
}


class CognitoAuthManager:
    """Manages Cognito authentication and token refresh."""
    
    def __init__(self, token_endpoint: str, client_id: str, client_secret: str):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        # Check if cached token is still valid
        if _token_cache['access_token'] and time.time() < _token_cache['expires_at']:
            return _token_cache['access_token']
        
        # Request new token
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'member-liability-api/read member-liability-api/write'
        }
        
        try:
            response = await self.http_client.post(
                self.token_endpoint,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            
            # Cache token with 5-minute buffer
            _token_cache['access_token'] = access_token
            _token_cache['expires_at'] = time.time() + expires_in - 300
            
            return access_token
            
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


class MemberBenefitsLiabilityAPI:
    """Client for Member Benefits & Liability APIs."""
    
    def __init__(self, base_url: str, auth_manager: CognitoAuthManager):
        self.base_url = base_url.rstrip('/')
        self.auth_manager = auth_manager
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request."""
        # Get access token
        access_token = await self.auth_manager.get_access_token()
        
        # Prepare request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = await self.http_client.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = await self.http_client.post(
                    url,
                    headers=headers,
                    json=data
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise Exception(
                f"API request failed with status {e.response.status_code}: {error_detail}"
            )
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    async def check_eligibility(
        self,
        member_id: str,
        service_date: str,
        benefit_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check member eligibility for benefits.
        
        Args:
            member_id: Unique member identifier
            service_date: Date of service (YYYY-MM-DD)
            benefit_code: Optional benefit code to check
        
        Returns:
            Eligibility information including status and coverage period
        """
        data = {
            'memberId': member_id,
            'serviceDate': service_date
        }
        
        if benefit_code:
            data['benefitCode'] = benefit_code
        
        return await self._make_request('POST', '/check-eligibility', data)
    
    async def get_member_benefits(
        self,
        member_id: str,
        benefit_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get member benefits information.
        
        Args:
            member_id: Unique member identifier
            benefit_type: Optional benefit type filter
        
        Returns:
            Benefits information including coverage details
        """
        data = {
            'memberId': member_id
        }
        
        if benefit_type:
            data['benefitType'] = benefit_type
        
        return await self._make_request('POST', '/member-benefits', data)
    
    async def calculate_liability(
        self,
        member_id: str,
        claim_id: str,
        service_code: Optional[str] = None,
        total_charges: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate member liability for a claim.
        
        Args:
            member_id: Unique member identifier
            claim_id: Unique claim identifier
            service_code: Optional service code
            total_charges: Optional total charges amount
        
        Returns:
            Liability calculation with breakdown
        """
        data = {
            'memberId': member_id,
            'claimId': claim_id
        }
        
        if service_code:
            data['serviceCode'] = service_code
        
        if total_charges is not None:
            data['totalCharges'] = total_charges
        
        return await self._make_request('POST', '/calculate-liability', data)
    
    async def lookup_order(self, order_id: str) -> Dict[str, Any]:
        """
        Look up order information.
        
        Args:
            order_id: Unique order identifier
        
        Returns:
            Order details and status
        """
        data = {
            'order_id': order_id
        }
        
        return await self._make_request('POST', '/order-lookup', data)
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Initialize MCP server
app = Server("member-benefits-liability")

# Initialize auth manager and API client (will be set in main)
auth_manager: Optional[CognitoAuthManager] = None
api_client: Optional[MemberBenefitsLiabilityAPI] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="check_member_eligibility",
            description=(
                "Check if a member is eligible for benefits on a specific service date. "
                "Returns eligibility status, enrollment status, coverage period, and applicable policy rules."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Unique member identifier (e.g., M123456)"
                    },
                    "service_date": {
                        "type": "string",
                        "description": "Date of service in YYYY-MM-DD format (e.g., 2024-03-15)"
                    },
                    "benefit_code": {
                        "type": "string",
                        "description": "Optional benefit code to check specific benefit eligibility"
                    }
                },
                "required": ["member_id", "service_date"]
            }
        ),
        Tool(
            name="get_member_benefits",
            description=(
                "Get detailed benefits information for a member. "
                "Returns coverage details, benefit limits, copays, deductibles, and out-of-pocket maximums."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Unique member identifier (e.g., M123456)"
                    },
                    "benefit_type": {
                        "type": "string",
                        "description": "Optional benefit type filter (e.g., medical, dental, vision)"
                    }
                },
                "required": ["member_id"]
            }
        ),
        Tool(
            name="calculate_member_liability",
            description=(
                "Calculate member liability for a claim. "
                "Returns total liability with breakdown of deductible, copay, coinsurance, "
                "and out-of-pocket maximum applied. Includes calculation steps and audit trail."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Unique member identifier (e.g., M123456)"
                    },
                    "claim_id": {
                        "type": "string",
                        "description": "Unique claim identifier (e.g., CLM789012)"
                    },
                    "service_code": {
                        "type": "string",
                        "description": "Optional service code (e.g., CPT code)"
                    },
                    "total_charges": {
                        "type": "number",
                        "description": "Optional total charges amount in dollars"
                    }
                },
                "required": ["member_id", "claim_id"]
            }
        ),
        Tool(
            name="lookup_order",
            description=(
                "Look up order information and details. "
                "Returns order status, details, and related information."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Unique order identifier"
                    }
                },
                "required": ["order_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    global api_client
    
    if not api_client:
        return [TextContent(
            type="text",
            text="ERROR: API client not initialized. Check configuration."
        )]
    
    try:
        if name == "check_member_eligibility":
            result = await api_client.check_eligibility(
                member_id=arguments["member_id"],
                service_date=arguments["service_date"],
                benefit_code=arguments.get("benefit_code")
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_member_benefits":
            result = await api_client.get_member_benefits(
                member_id=arguments["member_id"],
                benefit_type=arguments.get("benefit_type")
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "calculate_member_liability":
            result = await api_client.calculate_liability(
                member_id=arguments["member_id"],
                claim_id=arguments["claim_id"],
                service_code=arguments.get("service_code"),
                total_charges=arguments.get("total_charges")
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "lookup_order":
            result = await api_client.lookup_order(
                order_id=arguments["order_id"]
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"ERROR: Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"ERROR: {str(e)}"
        )]


async def main():
    """Main entry point."""
    global auth_manager, api_client
    
    # Validate configuration
    if not GATEWAY_API_URL:
        print("ERROR: GATEWAY_API_URL environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not COGNITO_TOKEN_ENDPOINT:
        print("ERROR: COGNITO_TOKEN_ENDPOINT environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not COGNITO_CLIENT_ID:
        print("ERROR: COGNITO_CLIENT_ID environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not COGNITO_CLIENT_SECRET:
        print("ERROR: COGNITO_CLIENT_SECRET environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Initialize auth manager and API client
    auth_manager = CognitoAuthManager(
        token_endpoint=COGNITO_TOKEN_ENDPOINT,
        client_id=COGNITO_CLIENT_ID,
        client_secret=COGNITO_CLIENT_SECRET
    )
    
    api_client = MemberBenefitsLiabilityAPI(
        base_url=GATEWAY_API_URL,
        auth_manager=auth_manager
    )
    
    # Run MCP server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
    
    # Cleanup
    await api_client.close()
    await auth_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
