#!/bin/bash

echo "🚀 SmartHire AWS Deployment Quick Start"
echo "========================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ Elastic Beanstalk CLI is not installed. Installing..."
    pip install awsebcli
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# AWS Deployment Configuration
AWS_DEPLOYMENT=true

# Database Configuration (update with your RDS endpoint)
DATABASE_URL=mysql+pymysql://admin:your_password@your-rds-endpoint:3306/smarthire

# Flask Secret Key (generate a secure one)
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Email Password (Gmail App Password)
EMAIL_PASSWORD=your_email_app_password_here
EOF
    echo "✅ Created .env file"
    echo "⚠️  Please update the DATABASE_URL with your RDS endpoint"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Set up AWS RDS database:"
echo "   - Go to AWS RDS Console"
echo "   - Create MySQL database (db.t3.micro for free tier)"
echo "   - Note down endpoint, username, and password"
echo "   - Update DATABASE_URL in .env file"
echo ""
echo "2. Deploy to Elastic Beanstalk:"
echo "   eb init smarthire --platform python-3.11 --region us-east-1"
echo "   eb create smarthire-prod --instance-type t2.micro"
echo "   eb deploy"
echo ""
echo "3. Set environment variables:"
echo "   eb setenv AWS_DEPLOYMENT=true"
echo "   eb setenv DATABASE_URL=\"your_rds_connection_string\""
echo "   eb setenv SECRET_KEY=\"your_secret_key\""
echo "   eb setenv GEMINI_API_KEY=\"your_gemini_key\""
echo "   eb setenv EMAIL_PASSWORD=\"your_email_password\""
echo ""
echo "📖 For detailed instructions, see: AWS_DEPLOYMENT_GUIDE.md" 