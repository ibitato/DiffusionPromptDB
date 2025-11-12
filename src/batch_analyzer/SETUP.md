# Setup Guide - Batch Analyzer

Complete setup guide for the Stable Diffusion Prompt Batch Analyzer.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [AWS Credentials Configuration](#aws-credentials-configuration)
4. [S3 Bucket Setup](#s3-bucket-setup)
5. [Bedrock Model Access](#bedrock-model-access)
6. [Application Configuration](#application-configuration)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.8+**: Check with `python --version`
- **pip**: Python package manager
- **AWS CLI** (recommended): `aws --version`
- **Git** (optional): For cloning the repository

### Required AWS Services

- **AWS Account** with billing enabled
- **AWS Bedrock** access
- **Amazon S3** bucket

## AWS Account Setup

### 1. Create AWS Account

If you don't have an AWS account:
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process
4. Add payment method (required for Bedrock access)

### 2. Create IAM User

For security, create a dedicated IAM user:

1. Go to IAM Console: https://console.aws.amazon.com/iam/
2. Click "Users" → "Add users"
3. Enter username: `bedrock-batch-analyzer`
4. Select "Access key - Programmatic access"
5. Click "Next: Permissions"

### 3. Attach IAM Policies

Create a custom policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:CreateModelInvocationJob",
        "bedrock:GetModelInvocationJob",
        "bedrock:ListModelInvocationJobs",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME/*",
        "arn:aws:s3:::YOUR-BUCKET-NAME"
      ]
    }
  ]
}
```

**Important**: Replace `YOUR-BUCKET-NAME` with your actual S3 bucket name.

Steps to create policy:
1. In IAM, go to "Policies" → "Create policy"
2. Click "JSON" tab
3. Paste the policy above (with your bucket name)
4. Click "Next: Tags" → "Next: Review"
5. Name: `BedrockBatchAnalyzerPolicy`
6. Click "Create policy"
7. Attach this policy to your IAM user

### 4. Get Access Keys

1. In IAM Users, select your user
2. Go to "Security credentials" tab
3. Click "Create access key"
4. Select "Command Line Interface (CLI)"
5. **Save the Access Key ID and Secret Access Key securely**
6. You'll need these for configuration

## AWS Credentials Configuration

Choose one of three methods to configure credentials:

### Method 1: AWS CLI (Recommended)

This is the most secure and convenient method.

#### Install AWS CLI

**Windows:**
```bash
# Download and run installer from:
# https://awscli.amazonaws.com/AWSCLIV2.msi
```

**macOS:**
```bash
brew install awscli
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### Configure Profile

```bash
aws configure --profile default
```

Enter when prompted:
- **AWS Access Key ID**: Your access key from IAM
- **AWS Secret Access Key**: Your secret key from IAM
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

#### Verify Configuration

```bash
# Test credentials
aws sts get-caller-identity --profile default

# Should output:
# {
#   "UserId": "AIDAI...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/bedrock-batch-analyzer"
# }
```

### Method 2: Environment Variables

Create a `.env` file:

```bash
cd src/batch_analyzer
cp .env.example .env
```

Edit `.env`:
```bash
# AWS Profile (if using AWS CLI)
AWS_PROFILE=default
AWS_DEFAULT_REGION=us-east-1

# OR Direct credentials (less secure)
# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# S3 Bucket
AWS_S3_BATCH_BUCKET=my-bedrock-batch-bucket
```

**Security Note**: Never commit `.env` file to git!

### Method 3: Config File

Edit `config.yaml`:
```yaml
aws:
  profile: "default"  # Preferred
  region: "us-east-1"
  
  # OR direct credentials (not recommended)
  # access_key_id: "AKIAIOSFODNN7EXAMPLE"
  # secret_access_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

## S3 Bucket Setup

### 1. Create S3 Bucket

**Via AWS Console:**
1. Go to S3 Console: https://s3.console.aws.amazon.com/
2. Click "Create bucket"
3. Enter bucket name: `my-bedrock-batch-analyzer`
   - Must be globally unique
   - Use lowercase, numbers, hyphens only
4. Select region: Same as your Bedrock region
5. Keep default settings (Block public access: ON)
6. Click "Create bucket"

**Via AWS CLI:**
```bash
# Create bucket
aws s3 mb s3://my-bedrock-batch-analyzer --region us-east-1

# Verify
aws s3 ls
```

### 2. Configure Bucket in Application

Edit `config.yaml`:
```yaml
batch:
  input_s3_uri: "s3://my-bedrock-batch-analyzer/batch-analyzer/input/"
  output_s3_uri: "s3://my-bedrock-batch-analyzer/batch-analyzer/output/"
```

Or use command line:
```bash
python run_analysis.py --s3-bucket my-bedrock-batch-analyzer
```

## Bedrock Model Access

### 1. Check Bedrock Availability

Bedrock is available in these regions:
- `us-east-1` (N. Virginia) ✓ Recommended
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

### 2. Request Model Access

1. Go to Bedrock Console: https://console.aws.amazon.com/bedrock/
2. Click "Model access" in left sidebar
3. Click "Modify model access" or "Enable specific models"
4. Find and enable:
   - **Claude 3.5 Sonnet** (anthropic.claude-3-5-sonnet-20241022-v2:0)
5. Click "Save changes"
6. Wait for "Access granted" status (usually instant)

### 3. Verify Model Access

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `claude-3-5-sonnet`)].{ID:modelId,Name:modelName}' \
  --output table

# Should show Claude 3.5 Sonnet models
```

## Application Configuration

### 1. Install Dependencies

```bash
cd src/batch_analyzer
pip install -r requirements.txt
```

### 2. Copy Configuration Template

```bash
cp config.yaml.example config.yaml
```

### 3. Edit Configuration

Open `config.yaml` and configure:

```yaml
# AWS Configuration
aws:
  profile: "default"           # Your AWS profile
  region: "us-east-1"         # Bedrock-enabled region

# Bedrock Configuration
bedrock:
  model_id: "anthropic.claude-3-5-sonnet-20241022-v2:0"
  max_tokens: 2000
  temperature: 0.0            # 0.0 for consistent categorization

# Batch Processing
batch:
  batch_size: 200             # Prompts per batch
  input_s3_uri: "s3://YOUR-BUCKET/batch-analyzer/input/"
  output_s3_uri: "s3://YOUR-BUCKET/batch-analyzer/output/"

# Input/Output Paths
paths:
  input_file: "../../json_data/prompts.jsonl"  # Path to your JSONL
  output_dir: "./results"
  logs_dir: "./logs"

# Processing Options
processing:
  dry_run: false              # Set true to test with 10 prompts
  dry_run_count: 10
```

**Important Settings:**
- Replace `YOUR-BUCKET` with your S3 bucket name
- Adjust `input_file` path to your JSONL file location
- Set `dry_run: true` for initial testing

## Verification

### Run Setup Verification

```bash
python verify_setup.py
```

This checks:
- ✓ Configuration file exists
- ✓ AWS credentials configured
- ✓ Bedrock connection successful
- ✓ Model available
- ✓ Input file exists
- ✓ S3 bucket configured
- ✓ Output directories accessible

Expected output:
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        Stable Diffusion Prompt Batch Analyzer           ║
║                                                          ║
║        Powered by AWS Bedrock & Claude Sonnet           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🔍 Verifying setup...

✓ Environment variables loaded
✓ Configuration file loaded

📋 Validating configuration...
✓ Configuration is valid

🔐 Checking AWS credentials...
   Profile: default
   Region: us-east-1
✓ AWS connection successful

🤖 Checking Bedrock model...
   Model ID: anthropic.claude-3-5-sonnet-20241022-v2:0
✓ Model is available

📁 Checking input file...
✓ Input file found: ../../json_data/prompts.jsonl
   Total prompts: 10,000
   Estimated cost (full run): $60.00 USD

📂 Checking output directory...
✓ Output directory ready: ./results

☁️  Checking S3 configuration...
   Input S3 URI: s3://my-bucket/batch-analyzer/input/
   Output S3 URI: s3://my-bucket/batch-analyzer/output/
✓ S3 URIs configured

============================================================
✅ Setup verification PASSED

You can now run:
  python run_analysis.py --dry-run    # Test with 10 prompts
  python run_analysis.py              # Full analysis
```

### Test Dry Run

```bash
python run_analysis.py --dry-run
```

This processes only 10 prompts to verify everything works.

## Troubleshooting

### Issue: "Config file not found"

**Solution:**
```bash
cp config.yaml.example config.yaml
# Then edit config.yaml
```

### Issue: "AWS connection failed: Unable to locate credentials"

**Solutions:**

1. **If using AWS CLI:**
   ```bash
   aws configure --profile default
   ```

2. **Check credentials file:**
   ```bash
   # Windows: C:\Users\USERNAME\.aws\credentials
   # Linux/Mac: ~/.aws/credentials
   
   cat ~/.aws/credentials
   # Should contain:
   # [default]
   # aws_access_key_id = YOUR_KEY
   # aws_secret_access_key = YOUR_SECRET
   ```

3. **Set environment variables:**
   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

### Issue: "Access denied" or "UnauthorizedOperation"

**Solution:**
1. Verify IAM user has required permissions
2. Check IAM policy is attached to user
3. Verify policy includes all required actions
4. Test with AWS CLI:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

### Issue: "Model not found" or "Model not accessible"

**Solution:**
1. Go to Bedrock Console → Model access
2. Enable Claude 3.5 Sonnet
3. Wait for "Access granted" status
4. Verify model ID in config.yaml matches exactly

### Issue: "Bucket does not exist"

**Solution:**
1. Create S3 bucket:
   ```bash
   aws s3 mb s3://your-bucket-name --region us-east-1
   ```
2. Update config.yaml with correct bucket name
3. Verify bucket exists:
   ```bash
   aws s3 ls
   ```

### Issue: "Input file not found"

**Solution:**
1. Check path in config.yaml
2. Use relative path from `src/batch_analyzer/` directory
3. Verify file exists:
   ```bash
   ls -la ../../json_data/prompts.jsonl
   ```

### Issue: Rate limits or throttling

**Solution:**
1. Reduce `batch_size` in config.yaml
2. Add delay between operations
3. Check AWS service quotas:
   - Bedrock: Model invocations per minute
   - S3: Request rate

### Issue: Batch job fails

**Solution:**
1. Check job status in AWS Console:
   - Go to Bedrock → Batch inference jobs
2. View error messages
3. Common causes:
   - Invalid S3 paths
   - Insufficient IAM permissions
   - Input file format errors
   - Model capacity issues

### Getting Help

1. **Run diagnostics:**
   ```bash
   python verify_setup.py
   python run_analysis.py --log-level DEBUG --dry-run
   ```

2. **Check logs:**
   ```bash
   cat logs/analysis_*.log
   ```

3. **Test AWS connectivity:**
   ```bash
   aws sts get-caller-identity
   aws bedrock list-foundation-models --region us-east-1
   aws s3 ls
   ```

4. **Review AWS documentation:**
   - [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
   - [Batch Inference Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html)

## Next Steps

Once setup is complete:

1. **Test with dry run:**
   ```bash
   python run_analysis.py --dry-run
   ```

2. **Run full analysis:**
   ```bash
   python run_analysis.py
   ```

3. **Monitor progress:**
   - Check AWS Bedrock Console for job status
   - Review logs in `logs/` directory

4. **Retrieve results:**
   ```bash
   python run_analysis.py --retrieve results/job_<timestamp>.json
   ```

See [README.md](README.md) for full usage documentation.
