#!/usr/bin/env python3
"""
Setup Verification Script

Verify that AWS credentials, Bedrock access, and configuration are correct.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.utils import (
    load_config,
    load_environment,
    validate_config,
    setup_logging,
    print_banner,
)
from core.bedrock_client import BedrockBatchClient
from core.batch_processor import BatchProcessor


def main():
    """Main verification function."""
    print_banner()
    print("\n🔍 Verifying setup...\n")

    all_ok = True

    # Load environment variables
    try:
        load_environment()
        print("✓ Environment variables loaded")
    except Exception as e:
        print(f"⚠ Warning loading environment: {e}")

    # Load configuration
    try:
        config = load_config("config.yaml")
        print("✓ Configuration file loaded")
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\nTo fix this:")
        print("  1. Copy config.yaml.example to config.yaml")
        print("  2. Edit config.yaml with your settings")
        return 1
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return 1

    # Validate configuration
    print("\n📋 Validating configuration...")
    valid, errors = validate_config(config)
    if not valid:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"   - {error}")
        all_ok = False
    else:
        print("✓ Configuration is valid")

    # Check AWS credentials
    print("\n🔐 Checking AWS credentials...")
    aws_config = config.get("aws", {})
    aws_profile = aws_config.get("profile")
    aws_region = aws_config.get("region", "us-east-1")

    print(f"   Profile: {aws_profile or 'default'}")
    print(f"   Region: {aws_region}")

    try:
        client = BedrockBatchClient(profile_name=aws_profile, region_name=aws_region)

        success, msg = client.test_connection()
        if success:
            print(f"✓ {msg}")
        else:
            print(f"❌ {msg}")
            all_ok = False

    except Exception as e:
        print(f"❌ Error testing AWS connection: {e}")
        all_ok = False

    # Check Bedrock model
    print("\n🤖 Checking Bedrock model...")
    bedrock_config = config.get("bedrock", {})
    model_id = bedrock_config.get("model_id")

    print(f"   Model ID: {model_id}")

    try:
        success, msg = client.check_model_available(model_id)
        if success:
            print(f"✓ {msg}")
        else:
            print(f"❌ {msg}")
            all_ok = False
    except Exception as e:
        print(f"❌ Error checking model: {e}")
        all_ok = False

    # Check input file
    print("\n📁 Checking input file...")
    paths_config = config.get("paths", {})
    input_file = paths_config.get("input_file")

    if input_file:
        input_path = Path(input_file)
        if input_path.exists():
            try:
                processor = BatchProcessor(str(input_path))
                count = processor.count_prompts()
                print(f"✓ Input file found: {input_path}")
                print(f"   Total prompts: {count:,}")

                # Show cost estimate for full run
                cost_info = processor.estimate_cost(count)
                print(
                    f"   Estimated cost (full run): ${cost_info['total_cost_usd']:.2f} USD"
                )

            except Exception as e:
                print(f"❌ Error reading input file: {e}")
                all_ok = False
        else:
            print(f"❌ Input file not found: {input_path}")
            all_ok = False
    else:
        print("❌ Input file not specified in config")
        all_ok = False

    # Check output directory
    print("\n📂 Checking output directory...")
    output_dir = paths_config.get("output_dir", "./results")
    output_path = Path(output_dir)

    try:
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory ready: {output_path}")
    except Exception as e:
        print(f"❌ Cannot create output directory: {e}")
        all_ok = False

    # Check S3 bucket configuration
    print("\n☁️  Checking S3 configuration...")
    batch_config = config.get("batch", {})
    input_s3 = batch_config.get("input_s3_uri")
    output_s3 = batch_config.get("output_s3_uri")

    if input_s3:
        print(f"   Input S3 URI: {input_s3}")
    if output_s3:
        print(f"   Output S3 URI: {output_s3}")

    if not input_s3 and not output_s3:
        print("⚠  Warning: No S3 URIs configured")
        print("   You'll need to specify an S3 bucket when running analysis")
        print("   Add 'input_s3_uri' and 'output_s3_uri' to config.yaml")
        print("   Example: s3://your-bucket-name/batch-analyzer/")
    else:
        print("✓ S3 URIs configured")

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Setup verification PASSED")
        print("\nYou can now run:")
        print("  python run_analysis.py --dry-run    # Test with 10 prompts")
        print("  python run_analysis.py              # Full analysis")
        return 0
    else:
        print("❌ Setup verification FAILED")
        print("\nPlease fix the issues above before running analysis.")
        print("\nFor help, see:")
        print("  - README.md")
        print("  - SETUP.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
