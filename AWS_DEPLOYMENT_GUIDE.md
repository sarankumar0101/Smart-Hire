# AWS Deployment Guide for SmartHire

This guide will help you deploy your SmartHire application to AWS using Elastic Beanstalk and RDS.

## Prerequisites

1. **AWS Account** with Free Tier access
2. **AWS CLI** installed and configured
3. **Elastic Beanstalk CLI** installed
4. **Python 3.11** or later

## Step 1: Install Required Tools

### Install AWS CLI
```bash
# Windows
curl "https://awscli.amazonaws.com/AWSCLIV2.msi" -o "AWSCLIV2.msi"
msiexec.exe /i AWSCLIV2.msi

# macOS
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Install Elastic Beanstalk CLI
```bash
pip install awsebcli
```

### Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your output format (json)
```

## Step 2: Set Up AWS RDS Database

1. **Go to AWS RDS Console**
   - Navigate to https://console.aws.amazon.com/rds/

2. **Create Database**
   - Click "Create database"
   - Choose "Standard create"
   - Select "MySQL" as engine
   - Choose "Free tier" template
   - Set database name: `smarthire`
   - Set master username: `admin`
   - Set master password: `your_secure_password`
   - Choose "db.t3.micro" instance class
   - Set storage: 20 GB
   - Enable "Public access" (for development)
   - Create new VPC security group
   - Click "Create database"

3. **Note Database Details**
   - Endpoint: `your-db-name.region.rds.amazonaws.com`
   - Port: 3306
   - Database name: `smarthire`
   - Username: `admin`
   - Password: `your_secure_password`

## Step 3: Configure Security Groups

1. **RDS Security Group**
   - Go to EC2 → Security Groups
   - Find your RDS security group
   - Add inbound rule: MySQL (3306) from your IP or 0.0.0.0/0

2. **Elastic Beanstalk Security Group**
   - Will be created automatically
   - Allows HTTP (80) and HTTPS (443)

## Step 4: Prepare Application for Deployment

1. **Update Environment Variables**
   ```bash
   # Run the deployment script
   python deploy_to_aws.py
   ```

2. **Update .env file with RDS details**
   ```env
   AWS_DEPLOYMENT=true
   DATABASE_URL=mysql+pymysql://admin:your_password@your-db-endpoint:3306/smarthire
   SECRET_KEY=your_secure_secret_key
   GEMINI_API_KEY=your_gemini_api_key
   EMAIL_PASSWORD=your_email_app_password
   ```

## Step 5: Deploy to Elastic Beanstalk

1. **Initialize EB Application**
   ```bash
   eb init smarthire --platform python-3.11 --region us-east-1
   ```

2. **Create Environment**
   ```bash
   eb create smarthire-prod --instance-type t2.micro
   ```

3. **Set Environment Variables**
   ```bash
   eb setenv AWS_DEPLOYMENT=true
   eb setenv DATABASE_URL="mysql+pymysql://admin:your_password@your-db-endpoint:3306/smarthire"
   eb setenv SECRET_KEY="your_secure_secret_key"
   eb setenv GEMINI_API_KEY="your_gemini_api_key"
   eb setenv EMAIL_PASSWORD="your_email_app_password"
   ```

4. **Deploy Application**
   ```bash
   eb deploy
   ```

## Step 6: Set Up Database Tables

1. **Access your deployed application**
   - Get the URL from Elastic Beanstalk console
   - Or run: `eb open`

2. **Initialize Database**
   ```bash
   # SSH into your EB instance
   eb ssh
   
   # Run database setup
   python setup_sqlite_database.py
   ```

## Step 7: Configure Domain (Optional)

1. **Register Domain** (if needed)
   - Use Route 53 or external registrar

2. **Configure SSL Certificate**
   ```bash
   eb config
   # Add SSL certificate configuration
   ```

## Step 8: Monitor and Maintain

1. **Monitor Application**
   - Use CloudWatch for logs and metrics
   - Set up alarms for errors and performance

2. **Backup Database**
   - RDS provides automated backups
   - Configure backup retention period

3. **Scale Application**
   - Use EB auto-scaling groups
   - Monitor costs and usage

## Cost Optimization (Free Tier)

### Free Tier Limits
- **EC2**: 750 hours/month (t2.micro)
- **RDS**: 750 hours/month (db.t3.micro)
- **Data Transfer**: 15 GB/month
- **Storage**: 20 GB (RDS)

### Cost Monitoring
1. **Set up AWS Budgets**
   - Go to AWS Budgets console
   - Create budget alerts

2. **Monitor Usage**
   - Check AWS Cost Explorer
   - Set up billing alerts

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check security group rules
   - Verify database endpoint
   - Ensure database is publicly accessible

2. **Application Won't Start**
   - Check EB logs: `eb logs`
   - Verify environment variables
   - Check application configuration

3. **Static Files Not Loading**
   - Verify .ebextensions configuration
   - Check file permissions
   - Ensure correct file paths

### Useful Commands

```bash
# View application logs
eb logs

# SSH into instance
eb ssh

# Check application status
eb status

# Open application in browser
eb open

# View environment configuration
eb config

# Terminate environment (when done)
eb terminate smarthire-prod
```

## Security Best Practices

1. **Use Strong Passwords**
   - Generate secure passwords for database
   - Use environment variables for secrets

2. **Enable HTTPS**
   - Configure SSL certificates
   - Redirect HTTP to HTTPS

3. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories

4. **Access Control**
   - Use IAM roles and policies
   - Limit database access

## Next Steps

1. **Set up CI/CD pipeline**
   - Use AWS CodePipeline
   - Connect to GitHub repository

2. **Add monitoring and alerting**
   - Set up CloudWatch alarms
   - Configure error tracking

3. **Implement backup strategy**
   - Configure RDS automated backups
   - Set up cross-region replication

4. **Optimize performance**
   - Use CDN for static files
   - Implement caching strategies

## Support

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Elastic Beanstalk**: https://docs.aws.amazon.com/elasticbeanstalk/
- **RDS Documentation**: https://docs.aws.amazon.com/rds/
- **AWS Support**: Available with paid plans 