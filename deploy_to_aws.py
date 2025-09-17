#!/usr/bin/env python3
"""
AWS Deployment Script for SmartHire
This script helps deploy the SmartHire application to AWS using Elastic Beanstalk and RDS.
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_aws_cli():
    """Check if AWS CLI is installed and configured."""
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ AWS CLI is installed")
            return True
        else:
            print("❌ AWS CLI is not installed")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI is not installed")
        return False

def check_eb_cli():
    """Check if Elastic Beanstalk CLI is installed."""
    try:
        result = subprocess.run(['eb', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Elastic Beanstalk CLI is installed")
            return True
        else:
            print("❌ Elastic Beanstalk CLI is not installed")
            return False
    except FileNotFoundError:
        print("❌ Elastic Beanstalk CLI is not installed")
        return False

def create_env_file():
    """Create .env file with AWS deployment settings."""
    env_content = """# AWS Deployment Configuration
AWS_DEPLOYMENT=true

# Database Configuration (will be updated with RDS endpoint)
DATABASE_URL=mysql+pymysql://username:password@your-rds-endpoint:3306/smarthire

# Flask Secret Key (generate a secure one)
SECRET_KEY=your_secure_secret_key_here

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Email Password (Gmail App Password)
EMAIL_PASSWORD=your_email_app_password_here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file for AWS deployment")
    print("⚠️  Please update the DATABASE_URL with your RDS endpoint")

def create_eb_application():
    """Create Elastic Beanstalk application."""
    print("🚀 Creating Elastic Beanstalk application...")
    
    # Initialize EB application
    subprocess.run(['eb', 'init', 'smarthire', '--platform', 'python-3.11', '--region', 'us-east-1'])
    
    # Create environment
    subprocess.run(['eb', 'create', 'smarthire-prod', '--instance-type', 't2.micro'])

def main():
    """Main deployment function."""
    print("🚀 AWS Deployment Setup for SmartHire")
    print("=" * 50)
    
    # Check prerequisites
    if not check_aws_cli():
        print("\n📝 Please install AWS CLI:")
        print("   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
        return
    
    if not check_eb_cli():
        print("\n📝 Please install Elastic Beanstalk CLI:")
        print("   pip install awsebcli")
        return
    
    # Create environment file
    create_env_file()
    
    print("\n📝 Next steps:")
    print("1. Set up AWS RDS database:")
    print("   - Go to AWS RDS Console")
    print("   - Create a MySQL database (db.t3.micro for free tier)")
    print("   - Note down the endpoint, username, and password")
    print("   - Update DATABASE_URL in .env file")
    print("\n2. Configure AWS credentials:")
    print("   aws configure")
    print("\n3. Deploy to Elastic Beanstalk:")
    print("   eb init")
    print("   eb create smarthire-prod")
    print("   eb deploy")
    print("\n4. Set environment variables in EB:")
    print("   eb setenv AWS_DEPLOYMENT=true")
    print("   eb setenv DATABASE_URL=your_rds_connection_string")
    print("   eb setenv SECRET_KEY=your_secret_key")
    print("   eb setenv GEMINI_API_KEY=your_gemini_key")
    print("   eb setenv EMAIL_PASSWORD=your_email_password")

if __name__ == "__main__":
    main() 