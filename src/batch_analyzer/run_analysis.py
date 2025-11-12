#!/usr/bin/env python3
"""
Batch Analysis Runner

Main script for analyzing Stable Diffusion prompts using AWS Bedrock.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.utils import (
    load_config,
    load_environment,
    setup_logging,
    print_banner,
    print_cost_estimate,
    get_s3_bucket_from_config,
)
from core.analyzer import PromptAnalyzer
from core.batch_processor import BatchProcessor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Stable Diffusion prompts using AWS Bedrock",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify setup first
  python verify_setup.py
  
  # Dry run with 10 prompts
  python run_analysis.py --dry-run
  
  # Full analysis
  python run_analysis.py
  
  # Retrieve results from completed job
  python run_analysis.py --retrieve results/job_20250112_075500.json
  
  # Resume from specific prompt ID
  python run_analysis.py --resume-from 1000
  
  # Specify S3 bucket
  python run_analysis.py --s3-bucket my-batch-bucket
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process only a small number of prompts for testing",
    )

    parser.add_argument(
        "--dry-run-count",
        type=int,
        default=10,
        help="Number of prompts for dry run (default: 10)",
    )

    parser.add_argument(
        "--resume-from", type=int, help="Resume processing from this prompt ID"
    )

    parser.add_argument(
        "--s3-bucket", type=str, help="S3 bucket name for batch processing"
    )

    parser.add_argument(
        "--retrieve",
        type=str,
        metavar="JOB_FILE",
        help="Retrieve results from a completed job (provide job info JSON file)",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    return parser.parse_args()


def run_analysis(args):
    """
    Run the analysis.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print_banner()

    # Load environment and configuration
    try:
        load_environment()
        config = load_config(args.config)
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        print("\nRun 'python verify_setup.py' to check your setup.")
        return 1

    # Setup logging
    log_config = config.get("logging", {})
    log_level = args.log_level or log_config.get("level", "INFO")
    log_format = log_config.get("format")

    # Create log file with timestamp
    if log_config.get("file_logging", True):
        logs_dir = Path(config.get("paths", {}).get("logs_dir", "./logs"))
        logs_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"analysis_{timestamp}.log"
    else:
        log_file = None

    setup_logging(log_level, str(log_file) if log_file else None, log_format)

    # Extract configuration
    aws_config = config.get("aws", {})
    bedrock_config = config.get("bedrock", {})
    batch_config = config.get("batch", {})
    paths_config = config.get("paths", {})
    processing_config = config.get("processing", {})

    # Determine dry run mode
    dry_run = args.dry_run or processing_config.get("dry_run", False)
    dry_run_count = args.dry_run_count or processing_config.get("dry_run_count", 10)

    # Determine S3 bucket
    s3_bucket = args.s3_bucket or get_s3_bucket_from_config(config)

    # Create analyzer
    try:
        analyzer = PromptAnalyzer(
            input_file=paths_config.get("input_file"),
            output_dir=paths_config.get("output_dir", "./results"),
            model_id=bedrock_config.get("model_id"),
            aws_profile=aws_config.get("profile"),
            aws_region=aws_config.get("region", "us-east-1"),
            batch_size=batch_config.get("batch_size", 200),
            max_tokens=bedrock_config.get("max_tokens", 2000),
            temperature=bedrock_config.get("temperature", 0.0),
        )
    except Exception as e:
        print(f"\n❌ Error initializing analyzer: {e}")
        return 1

    # Verify setup
    print("\n🔍 Verifying setup...")
    all_ok, messages = analyzer.verify_setup()

    for msg in messages:
        print(f"   {msg}")

    if not all_ok:
        print("\n❌ Setup verification failed. Please fix issues above.")
        return 1

    print("\n✅ Setup verified!\n")

    # Handle retrieve mode
    if args.retrieve:
        print(f"📥 Retrieving results from job: {args.retrieve}\n")
        success, msg = analyzer.retrieve_results(args.retrieve)

        if success:
            print(f"\n✅ {msg}")
            return 0
        else:
            print(f"\n❌ {msg}")
            return 1

    # Show mode and cost estimate
    if dry_run:
        print(f"🧪 Running in DRY RUN mode (processing {dry_run_count} prompts)")
    else:
        print("🚀 Running in FULL mode (processing all prompts)")

    # Get cost estimate
    processor = analyzer.processor
    total_prompts = processor.count_prompts()

    if dry_run:
        prompts_to_process = min(dry_run_count, total_prompts)
    else:
        prompts_to_process = total_prompts

    if args.resume_from:
        print(f"   Resuming from prompt ID: {args.resume_from}")
        # Adjust count for resumed processing
        prompts_to_process = total_prompts - args.resume_from + 1

    cost_estimate = processor.estimate_cost(prompts_to_process)
    print_cost_estimate(cost_estimate)

    # Confirm before proceeding
    if not dry_run:
        response = input(
            "\n⚠️  This will start a batch job that may take hours to complete.\nProceed? (yes/no): "
        )
        if response.lower() not in ["yes", "y"]:
            print("\nAnalysis cancelled.")
            return 0

    # Check S3 bucket
    if not s3_bucket:
        print("\n❌ S3 bucket not specified.")
        print("\nPlease either:")
        print("  1. Add 'input_s3_uri' and 'output_s3_uri' to config.yaml")
        print("  2. Set AWS_S3_BATCH_BUCKET environment variable")
        print("  3. Use --s3-bucket command line option")
        print("\nExample: python run_analysis.py --s3-bucket my-bucket-name")
        return 1

    print(f"\n📦 Using S3 bucket: {s3_bucket}")

    # Run analysis
    print("\n🔄 Starting batch analysis...\n")

    try:
        success, msg = analyzer.analyze_prompts(
            dry_run=dry_run,
            dry_run_count=dry_run_count,
            resume_from_id=args.resume_from,
            s3_bucket=s3_bucket,
        )

        if success:
            print(f"\n✅ {msg}")
            print("\n" + "=" * 60)
            print("NEXT STEPS:")
            print("=" * 60)
            print("\n1. Wait for the batch job to complete (may take several hours)")
            print("\n2. Check job status in AWS Console:")
            print("   https://console.aws.amazon.com/bedrock/")
            print("\n3. When complete, retrieve results:")
            print("   python run_analysis.py --retrieve <job_info_file>")
            print("\n4. Job info saved in results/ directory")
            print("=" * 60)
            return 0
        else:
            print(f"\n❌ {msg}")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    args = parse_args()
    exit_code = run_analysis(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
