# Cleanup Guide - AWS Resources

This document lists all AWS resources created by the Batch Analyzer and provides instructions for cleanup.

## Created AWS Resources

### 1. S3 Bucket

**Bucket Name:** `diffusion-prompt-analyzer-20251211`  
**Region:** `us-east-1`  
**Purpose:** Stores batch job input/output files

**Contents:**
- `batch-analyzer/input/` - Batch job input files (JSONL)
- `batch-analyzer/output/` - Batch job output results

**To Delete:**

```bash
# Delete all objects in bucket first
aws s3 rm s3://diffusion-prompt-analyzer-20251211 --recursive --region us-east-1

# Then delete the bucket
aws s3 rb s3://diffusion-prompt-analyzer-20251211 --region us-east-1
```

### 2. IAM Role

**Role Name:** `BedrockBatchAnalyzerRole`  
**ARN:** `arn:aws:iam::029423023787:role/BedrockBatchAnalyzerRole`  
**Purpose:** Allows Bedrock to access S3 bucket for batch processing

**Attached Policies:**
- `S3AccessPolicy` (inline policy)

**Policy Details:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::diffusion-prompt-analyzer-20251211/*",
        "arn:aws:s3:::diffusion-prompt-analyzer-20251211"
      ]
    }
  ]
}
```

**To Delete:**

```bash
# First, delete the inline policy
aws iam delete-role-policy \
  --role-name BedrockBatchAnalyzerRole \
  --policy-name S3AccessPolicy

# Then delete the role
aws iam delete-role --role-name BedrockBatchAnalyzerRole
```

### 3. Bedrock Batch Jobs

**Job Naming Pattern:** `prompt-analysis-YYYYMMDD-HHMMSS`  
**Example ARN:** `arn:aws:bedrock:us-east-1:029423023787:model-invocation-job/uzatv6zifcen`

**Note:** Batch jobs cannot be deleted, but they expire automatically after 90 days.

**To List Active Jobs:**
```bash
aws bedrock list-model-invocation-jobs --region us-east-1
```

## Complete Cleanup Script

Save this as `cleanup_aws_resources.sh`:

```bash
#!/bin/bash

# Cleanup script for Batch Analyzer AWS resources
# Run this script when you're done with the analysis

echo "Starting AWS cleanup for Batch Analyzer..."

# 1. Delete S3 bucket contents and bucket
echo "Deleting S3 bucket..."
aws s3 rm s3://diffusion-prompt-analyzer-20251211 --recursive --region us-east-1
aws s3 rb s3://diffusion-prompt-analyzer-20251211 --region us-east-1

# 2. Delete IAM role policy
echo "Deleting IAM role policy..."
aws iam delete-role-policy \
  --role-name BedrockBatchAnalyzerRole \
  --policy-name S3AccessPolicy

# 3. Delete IAM role
echo "Deleting IAM role..."
aws iam delete-role --role-name BedrockBatchAnalyzerRole

echo "Cleanup complete!"
echo "Note: Batch jobs will expire automatically after 90 days."
```

## Before Cleanup

**Important:** Make sure to download all analysis results before running cleanup!

1. Check if any batch jobs are still running:
   ```bash
   python check_job_status.py
   ```

2. Download results if job is completed:
   ```bash
   python run_analysis.py --retrieve results/job_<timestamp>.json
   ```

3. Backup results locally:
   ```bash
   # Copy results to a safe location
   cp -r results/ /path/to/backup/
   ```

## Cost Considerations

After cleanup:
- **S3**: No more storage costs
- **IAM Role**: Free (no charges)
- **Batch Jobs**: Completed jobs have no ongoing costs

## Verification

After running cleanup, verify resources are deleted:

```bash
# Check S3 bucket
aws s3 ls | grep diffusion-prompt-analyzer

# Check IAM role
aws iam get-role --role-name BedrockBatchAnalyzerRole 2>&1 | grep NoSuchEntity

# Should return "NoSuchEntity" error if successfully deleted
```

## Re-creating Resources

If you need to run analysis again later:

1. Re-run the setup steps from SETUP.md
2. Or use the convenience script:
   ```bash
   python verify_setup.py  # Will detect missing resources
   ```

## Support

If you encounter issues during cleanup:
1. Check AWS Console for resource status
2. Verify you have necessary IAM permissions to delete resources
3. Contact AWS Support if resources are stuck in "deleting" state
