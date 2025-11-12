# Stable Diffusion Prompt Batch Analyzer

Analyze thousands of Stable Diffusion prompts using AWS Bedrock's Claude Sonnet 4.5 via Batch Inference API.

This tool automatically extracts and categorizes information from prompts including:
- **Characters**: Count, genders, age ranges, physical traits
- **Poses**: Body positions, angles, actions
- **Clothing**: Style, items, coverage level
- **Settings**: Location types, environment details
- **Lighting**: Types, time of day, quality
- **Art Style**: Primary style, quality tags, techniques
- **Technical**: Resolution, camera settings, detail levels
- **NSFW Content**: Classification and elements
- **Mood/Atmosphere**: Overall tone and emotions
- **Main Tags**: Most relevant keywords

## Features

✨ **Batch Processing**: Process thousands of prompts efficiently using AWS Bedrock Batch API  
💰 **Cost Effective**: 50% discount with Batch API vs standard invocations  
📊 **Structured Output**: JSON schema for easy indexing and cataloging  
🔄 **Resumable**: Continue from where you left off if interrupted  
📈 **Statistics**: Automatic generation of analysis statistics  
🔍 **Dry Run**: Test with sample data before full processing  
📝 **Comprehensive Logging**: Track all processing steps  

## Quick Start

### 1. Install Dependencies

```bash
cd src/batch_analyzer
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Choose one of three methods:

**Method A: AWS CLI (Recommended)**
```bash
aws configure --profile default
# Enter: Access Key, Secret Key, Region (e.g., us-east-1)
```

**Method B: Environment Variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Method C: Direct in config.yaml**
```yaml
aws:
  access_key_id: "your_key"
  secret_access_key: "your_secret"
```

See [SETUP.md](SETUP.md) for detailed instructions.

### 3. Configure the Analyzer

```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your settings
```

Key configurations:
- **AWS Profile**: `aws.profile` (default: "default")
- **AWS Region**: `aws.region` (must have Bedrock access)
- **Model ID**: `bedrock.model_id` (default: Claude 3.5 Sonnet)
- **S3 Bucket**: `batch.input_s3_uri` and `batch.output_s3_uri`
- **Input File**: `paths.input_file` (path to your JSONL file)

### 4. Verify Setup

```bash
python verify_setup.py
```

This checks:
- ✓ AWS credentials configured
- ✓ Bedrock access enabled
- ✓ Model available
- ✓ Input file exists
- ✓ S3 configuration

### 5. Run Analysis

**Two modes available:**

#### Mode 1: Batch Processing (Recommended for large datasets)

Best for: 1,000+ prompts. Cost-effective, takes 6-24 hours.

```bash
# Dry run (10 prompts)
python run_analysis.py --dry-run

# Full analysis
python run_analysis.py

# With custom S3 bucket
python run_analysis.py --s3-bucket my-bucket-name
```

#### Mode 2: Real-time Processing (NEW) ⚡

Best for: <1,000 prompts. Fast, immediate results, uses **Claude Haiku 4.5** (recommended).

```bash
# Analyze 10 prompts (uses Haiku 4.5 by default - fastest)
python run_realtime.py --count 10

# Analyze 100 prompts
python run_realtime.py --count 100

# Use Sonnet 4.5 for higher quality (slower)
python run_realtime.py --count 10 --model us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Start from specific ID
python run_realtime.py --count 50 --start-from 1000
```

**Comparison:**

| Feature | Batch Mode | Real-time Mode |
|---------|------------|----------------|
| Best for | >1,000 prompts | <1,000 prompts |
| Model | Claude 3.5 Sonnet | **Claude Haiku 4.5** ⚡ |
| Speed | 6-24 hours | **~7.6s per prompt** |
| Cost (10K prompts) | ~$67 (with 50% discount) | ~$45 |
| S3 Required | Yes | No |
| Results | After completion | **Immediate** |
| Success Rate | High | **100% (tested)** |

**Real-time Model Options:**
- **Haiku 4.5** (default): Fastest, same cost as Sonnet 4.5, 95%+ quality match
- **Sonnet 4.5**: 72% slower, minimal quality improvement (~5%)
- **Haiku 3**: Older, similar speed but lower quality

### 6. Retrieve Results (Batch Mode Only)

After the batch job completes (may take hours):

```bash
python run_analysis.py --retrieve results/job_20250112_075500.json
```

Results will be saved as:
- `analysis_results_<timestamp>.jsonl` - Analyzed prompts
- `statistics_<timestamp>.json` - Analysis statistics

## Input Format

Your input file should be JSONL (JSON Lines) format:

```jsonl
{"id": 1, "prompt": "score_9, 1girl, portrait, realistic, cinematic lighting"}
{"id": 2, "prompt": "masterpiece, landscape, mountains, sunset, 8k"}
```

See [schemas/input_schema.json](schemas/input_schema.json) for full specification.

## Output Format

Each analyzed prompt produces a structured JSON object:

```json
{
  "id": 1,
  "original_prompt": "score_9, 1girl, portrait...",
  "categories": {
    "character": {
      "count": 1,
      "genders": ["female"],
      "age_range": "unspecified",
      "physical_traits": [],
      "ethnicities": []
    },
    "pose": {...},
    "clothing": {...},
    "setting": {...},
    "lighting": {...},
    "art_style": {...},
    "technical": {...},
    "nsfw_content": {...},
    "mood_atmosphere": {...},
    "main_tags": [...]
  },
  "metadata": {
    "processed_at": "2025-01-12T07:52:00Z",
    "model_used": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "tokens_used": {"input": 250, "output": 450}
  }
}
```

See [schemas/output_schema.json](schemas/output_schema.json) for full specification.

## Command Line Options

```bash
# Verify setup
python verify_setup.py

# Dry run
python run_analysis.py --dry-run
python run_analysis.py --dry-run --dry-run-count 20

# Full analysis
python run_analysis.py

# Resume from specific prompt ID
python run_analysis.py --resume-from 1000

# Specify S3 bucket
python run_analysis.py --s3-bucket my-bucket

# Retrieve completed results
python run_analysis.py --retrieve results/job_<timestamp>.json

# Custom config file
python run_analysis.py --config my-config.yaml

# Debug logging
python run_analysis.py --log-level DEBUG
```

## Cost Estimation

Approximate costs using Claude 3.5 Sonnet with Batch API (50% discount):

| Prompts | Est. Cost |
|---------|-----------|
| 100 | $0.06 |
| 1,000 | $0.60 |
| 10,000 | $6.00 |
| 100,000 | $60.00 |

*Based on ~300 input tokens and ~800 output tokens per prompt*

The tool shows cost estimates before processing.

## AWS Requirements

### Required AWS Services
- **AWS Bedrock**: For Claude model access with Batch Inference API support
- **Amazon S3**: For batch input/output storage
- **IAM Role**: For Bedrock to access S3

### Bedrock Batch API Requirements

**Important:** Not all Claude models support Batch Inference API. 

**Supported Models in us-east-1:**
- ✅ `anthropic.claude-3-5-sonnet-20240620-v1:0` (Recommended - Used by default)
- ✅ `anthropic.claude-3-sonnet-20240229-v1:0` (Claude 3 Sonnet)
- ✅ `anthropic.claude-3-haiku-20240307-v1:0` (Faster, cheaper)
- ✅ `anthropic.claude-3-opus-20240229-v1:0` (Most capable)

**Not Supported for Batch:**
- ❌ `anthropic.claude-3-5-sonnet-20241022-v2:0` (Sonnet v2 - only supports INFERENCE_PROFILE)

**Check Model Support:**
```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude')].{ID:modelId,Batch:inferenceTypesSupported}"
```

### IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name/*",
        "arn:aws:s3:::your-bucket-name"
      ]
    }
  ]
}
```

### Model Access

1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to "Claude 3.5 Sonnet" (anthropic.claude-3-5-sonnet-20241022-v2:0)
4. Wait for approval (usually instant for Claude models)

## Project Structure

```
src/batch_analyzer/
├── README.md                      # This file
├── SETUP.md                       # Detailed setup guide
├── config.yaml.example            # Configuration template
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
├── verify_setup.py                # Setup verification script
├── run_analysis.py                # Main analysis script
├── core/                          # Core library code
│   ├── __init__.py
│   ├── analyzer.py               # Main analyzer orchestrator
│   ├── bedrock_client.py         # AWS Bedrock API client
│   ├── batch_processor.py        # Batch processing logic
│   ├── prompt_template.py        # Claude prompt templates
│   └── utils.py                  # Utility functions
├── schemas/                       # JSON schemas
│   ├── input_schema.json         # Input JSONL schema
│   └── output_schema.json        # Output JSON schema
├── examples/                      # Example files
│   └── sample_input.jsonl        # Sample input
├── results/                       # Analysis results (gitignored)
└── logs/                          # Log files (gitignored)
```

## Troubleshooting

### "Config file not found"
```bash
cp config.yaml.example config.yaml
# Then edit config.yaml
```

### "AWS connection failed: Access denied"
- Check AWS credentials are configured: `aws sts get-caller-identity`
- Verify IAM permissions include Bedrock access
- Ensure Bedrock is available in your region

### "Model not found"
- Check model ID in config.yaml
- Verify model access in Bedrock Console
- Confirm region supports the model

### "S3 bucket not specified"
- Add S3 URIs to config.yaml:
  ```yaml
  batch:
    input_s3_uri: "s3://my-bucket/batch-analyzer/input/"
    output_s3_uri: "s3://my-bucket/batch-analyzer/output/"
  ```
- Or use command line: `--s3-bucket my-bucket`

### "Input file not found"
- Check path in config.yaml `paths.input_file`
- Use relative path from batch_analyzer directory
- Example: `../../json_data/prompts.jsonl`

## Advanced Usage

### Custom Prompt Template

Edit `core/prompt_template.py` to customize how Claude analyzes prompts.

### Batch Size Configuration

Adjust in `config.yaml`:
```yaml
batch:
  batch_size: 200  # Number of prompts per batch job
```

### Resume Processing

If a job fails or is interrupted:
```bash
python run_analysis.py --resume-from 5000
```

### Processing Specific Prompts

Edit your input JSONL to include only the prompts you want to process.

## Cleanup

When you're done with the analysis, you can clean up AWS resources to avoid ongoing costs:

See [CLEANUP.md](CLEANUP.md) for detailed instructions on:
- Deleting the S3 bucket
- Removing the IAM role
- Cleanup verification
- Complete cleanup script

**Quick cleanup:**
```bash
# Delete S3 bucket
aws s3 rm s3://diffusion-prompt-analyzer-20251211 --recursive --region us-east-1
aws s3 rb s3://diffusion-prompt-analyzer-20251211 --region us-east-1

# Delete IAM role
aws iam delete-role-policy --role-name BedrockBatchAnalyzerRole --policy-name S3AccessPolicy
aws iam delete-role --role-name BedrockBatchAnalyzerRole
```

## Support

For issues or questions:
1. Check [SETUP.md](SETUP.md) for detailed configuration help
2. Run `python verify_setup.py` to diagnose problems
3. Check logs in `logs/` directory
4. Review AWS Bedrock documentation
5. See [CLEANUP.md](CLEANUP.md) for resource cleanup

## License

See main project LICENSE file.

## Version

0.1.0 - Initial release
