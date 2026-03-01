#!/bin/bash

# Benefits Member Liability Agent - Deployment Script
# This script automates the deployment of Lambda functions and Bedrock Agent

set -e  # Exit on error

echo "=========================================="
echo "Benefits Member Liability Agent Deployment"
echo "=========================================="
echo ""

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
LAMBDA_ROLE_NAME="BenefitsMemberLiabilityLambdaRole"
AGENT_ROLE_NAME="BenefitsMemberLiabilityAgentRole"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Please install AWS CLI first."
    exit 1
fi
print_success "AWS CLI found"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3 first."
    exit 1
fi
print_success "Python 3 found"

if ! command -v zip &> /dev/null; then
    print_error "zip command not found. Please install zip utility."
    exit 1
fi
print_success "zip utility found"

# Get AWS account ID
echo ""
echo "Getting AWS account information..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ -z "$AWS_ACCOUNT_ID" ]; then
    print_error "Failed to get AWS account ID. Check your AWS credentials."
    exit 1
fi
print_success "AWS Account ID: $AWS_ACCOUNT_ID"
print_success "AWS Region: $AWS_REGION"

# Step 1: Create Lambda execution role
echo ""
echo "Step 1: Creating Lambda execution role..."

LAMBDA_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${LAMBDA_ROLE_NAME}"

# Check if role exists
if aws iam get-role --role-name "$LAMBDA_ROLE_NAME" &> /dev/null; then
    print_warning "Lambda role already exists: $LAMBDA_ROLE_NAME"
else
    # Create trust policy
    cat > /tmp/lambda-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create role
    aws iam create-role \
        --role-name "$LAMBDA_ROLE_NAME" \
        --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
        --description "Execution role for Benefits Member Liability Lambda functions"
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name "$LAMBDA_ROLE_NAME" \
        --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    
    print_success "Created Lambda execution role"
    
    # Wait for role to be available
    echo "Waiting for IAM role to propagate..."
    sleep 10
fi

# Step 2: Package and deploy Lambda functions
echo ""
echo "Step 2: Packaging Lambda functions..."

# Package check_eligibility Lambda
echo "Packaging check_eligibility Lambda..."
zip -j check_eligibility.zip lambda_check_eligibility.py
print_success "Packaged check_eligibility.zip"

# Package calculate_liability Lambda
echo "Packaging calculate_liability Lambda..."
zip -j calculate_liability.zip lambda_calculate_liability.py
print_success "Packaged calculate_liability.zip"

# Deploy check_eligibility Lambda
echo ""
echo "Deploying check_eligibility Lambda..."
if aws lambda get-function --function-name member-liability-check-eligibility &> /dev/null; then
    print_warning "Lambda function already exists, updating code..."
    aws lambda update-function-code \
        --function-name member-liability-check-eligibility \
        --zip-file fileb://check_eligibility.zip \
        --region "$AWS_REGION"
else
    aws lambda create-function \
        --function-name member-liability-check-eligibility \
        --runtime python3.9 \
        --role "$LAMBDA_ROLE_ARN" \
        --handler lambda_check_eligibility.lambda_handler \
        --zip-file fileb://check_eligibility.zip \
        --timeout 30 \
        --memory-size 256 \
        --region "$AWS_REGION" \
        --description "Check member eligibility for benefits"
fi
print_success "Deployed check_eligibility Lambda"

# Deploy calculate_liability Lambda
echo ""
echo "Deploying calculate_liability Lambda..."
if aws lambda get-function --function-name member-liability-calculate &> /dev/null; then
    print_warning "Lambda function already exists, updating code..."
    aws lambda update-function-code \
        --function-name member-liability-calculate \
        --zip-file fileb://calculate_liability.zip \
        --region "$AWS_REGION"
else
    aws lambda create-function \
        --function-name member-liability-calculate \
        --runtime python3.9 \
        --role "$LAMBDA_ROLE_ARN" \
        --handler lambda_calculate_liability.lambda_handler \
        --zip-file fileb://calculate_liability.zip \
        --timeout 30 \
        --memory-size 256 \
        --region "$AWS_REGION" \
        --description "Calculate member liability amounts"
fi
print_success "Deployed calculate_liability Lambda"

# Get Lambda ARNs
ELIGIBILITY_LAMBDA_ARN=$(aws lambda get-function --function-name member-liability-check-eligibility --query 'Configuration.FunctionArn' --output text --region "$AWS_REGION")
LIABILITY_LAMBDA_ARN=$(aws lambda get-function --function-name member-liability-calculate --query 'Configuration.FunctionArn' --output text --region "$AWS_REGION")

echo ""
print_success "Lambda ARNs:"
echo "  Eligibility: $ELIGIBILITY_LAMBDA_ARN"
echo "  Liability: $LIABILITY_LAMBDA_ARN"

# Step 3: Create Bedrock Agent
echo ""
echo "Step 3: Creating Bedrock Agent..."
print_warning "NOTE: You need to manually update the Lambda ARNs in create_agent.py"
print_warning "Replace REGION and ACCOUNT_ID with actual values:"
echo "  Region: $AWS_REGION"
echo "  Account ID: $AWS_ACCOUNT_ID"
echo ""
print_warning "Then run: python3 create_agent.py"

# Cleanup
echo ""
echo "Cleaning up temporary files..."
rm -f /tmp/lambda-trust-policy.json
rm -f check_eligibility.zip
rm -f calculate_liability.zip
print_success "Cleanup complete"

echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo "✓ Lambda execution role created/verified"
echo "✓ Lambda functions deployed"
echo ""
echo "Next steps:"
echo "1. Update Lambda ARNs in create_agent.py"
echo "2. Run: python3 create_agent.py"
echo "3. Test the agent in AWS Bedrock Console"
echo ""
print_success "Deployment script completed!"
