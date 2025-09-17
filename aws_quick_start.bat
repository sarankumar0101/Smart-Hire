@echo off
echo 🚀 SmartHire AWS Deployment Quick Start
echo ========================================

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI is not installed. Please install it first:
    echo    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    pause
    exit /b 1
)

REM Check if EB CLI is installed
eb --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Elastic Beanstalk CLI is not installed. Installing...
    pip install awsebcli
)

REM Check if AWS credentials are configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS credentials not configured. Please run:
    echo    aws configure
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # AWS Deployment Configuration
        echo AWS_DEPLOYMENT=true
        echo.
        echo # Database Configuration ^(update with your RDS endpoint^)
        echo DATABASE_URL=mysql+pymysql://admin:your_password@your-rds-endpoint:3306/smarthire
        echo.
        echo # Flask Secret Key ^(generate a secure one^)
        echo SECRET_KEY=your_secure_secret_key_here
        echo.
        echo # Gemini API Key
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Email Password ^(Gmail App Password^)
        echo EMAIL_PASSWORD=your_email_app_password_here
    ) > .env
    echo ✅ Created .env file
    echo ⚠️  Please update the DATABASE_URL with your RDS endpoint
)

echo.
echo 📋 Next Steps:
echo 1. Set up AWS RDS database:
echo    - Go to AWS RDS Console
echo    - Create MySQL database ^(db.t3.micro for free tier^)
echo    - Note down endpoint, username, and password
echo    - Update DATABASE_URL in .env file
echo.
echo 2. Deploy to Elastic Beanstalk:
echo    eb init smarthire --platform python-3.11 --region us-east-1
echo    eb create smarthire-prod --instance-type t2.micro
echo    eb deploy
echo.
echo 3. Set environment variables:
echo    eb setenv AWS_DEPLOYMENT=true
echo    eb setenv DATABASE_URL="your_rds_connection_string"
echo    eb setenv SECRET_KEY="your_secret_key"
echo    eb setenv GEMINI_API_KEY="your_gemini_key"
echo    eb setenv EMAIL_PASSWORD="your_email_password"
echo.
echo 📖 For detailed instructions, see: AWS_DEPLOYMENT_GUIDE.md
pause 