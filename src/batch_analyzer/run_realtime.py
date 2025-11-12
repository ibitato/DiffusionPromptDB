#!/usr/bin/env python3
"""
Real-time Analysis Runner

Analyze Stable Diffusion prompts in real-time using AWS Bedrock.
Uses Claude 3.5 Haiku for fast processing.
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
)
from core.realtime_analyzer import RealtimeAnalyzer
from core.batch_processor import BatchProcessor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze prompts in real-time using AWS Bedrock (Claude 3.5 Haiku)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze 10 prompts (fast test)
  python run_realtime.py --count 10
  
  # Analyze 100 prompts
  python run_realtime.py --count 100
  
  # Analyze all prompts (use batch mode instead for large datasets)
  python run_realtime.py --all
  
  # Start from specific prompt ID
  python run_realtime.py --count 50 --start-from 1000
  
  # Use specific model
  python run_realtime.py --count 20 --model anthropic.claude-3-sonnet-20240229-v1:0

Note: For large datasets (>1000 prompts), use run_analysis.py (batch mode) instead.
        """,
    )

    parser.add_argument("--count", type=int, help="Number of prompts to analyze")

    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all prompts (warning: may take hours and be expensive)",
    )

    parser.add_argument("--start-from", type=int, help="Start from this prompt ID")

    parser.add_argument(
        "--model",
        type=str,
        default="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        help="Bedrock model ID or Inference Profile (default: Claude Haiku 4.5)",
    )

    parser.add_argument(
        "--config", type=str, default="config.yaml", help="Path to configuration file"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    parser.add_argument(
        "--no-progress", action="store_true", help="Disable progress bar"
    )

    return parser.parse_args()


def run_realtime_analysis(args):
    """
    Run real-time analysis.

    Args:
        args: Command line arguments

    Returns:
        Exit code
    """
    print_banner()
    print("\n⚡ Real-time Analysis Mode (Claude 3.5 Haiku)\n")

    # Load configuration
    try:
        load_environment()
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return 1

    # Setup logging
    log_config = config.get("logging", {})
    log_level = args.log_level or log_config.get("level", "INFO")
    logs_dir = Path(config.get("paths", {}).get("logs_dir", "./logs"))
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = logs_dir / f"realtime_{timestamp}.log"

    setup_logging(log_level, str(log_file), log_config.get("format"))

    # Extract configuration
    aws_config = config.get("aws", {})
    paths_config = config.get("paths", {})

    # Determine number of prompts
    if args.all:
        max_count = None
        print("⚠️  Warning: Analyzing ALL prompts in real-time")
        print("   This may take hours and cost more than batch mode.")
        print("   Consider using run_analysis.py (batch mode) instead.\n")
    elif args.count:
        max_count = args.count
        print(f"📊 Analyzing {max_count} prompts\n")
    else:
        print("❌ You must specify either --count N or --all")
        print("   Example: python run_realtime.py --count 10")
        return 1

    # Create processor to read prompts
    try:
        processor = BatchProcessor(
            input_file=paths_config.get("input_file"),
            batch_size=1,  # Not used in realtime
        )
    except Exception as e:
        print(f"❌ Error initializing processor: {e}")
        return 1

    # Count prompts
    total_prompts = processor.count_prompts()
    prompts_to_process = max_count if max_count else total_prompts
    prompts_to_process = min(prompts_to_process, total_prompts)

    print(f"Total prompts in file: {total_prompts:,}")
    print(f"Prompts to process: {prompts_to_process:,}\n")

    # Create analyzer
    try:
        analyzer = RealtimeAnalyzer(
            aws_profile=aws_config.get("profile"),
            aws_region=aws_config.get("region", "us-east-1"),
            model_id=args.model,
            max_tokens=2000,
            temperature=0.0,
        )
    except Exception as e:
        print(f"❌ Error initializing analyzer: {e}")
        return 1

    # Show cost estimate
    cost_estimate = analyzer.estimate_cost(prompts_to_process)
    print_cost_estimate(cost_estimate)

    # Confirm
    if prompts_to_process > 100:
        response = input(f"\n⚠️  Process {prompts_to_process:,} prompts? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Analysis cancelled.")
            return 0

    # Read prompts
    print("\n📖 Reading prompts...")
    prompts = list(
        processor.read_prompts(start_id=args.start_from, max_count=max_count)
    )

    if not prompts:
        print("❌ No prompts to process")
        return 1

    print(f"✓ Loaded {len(prompts)} prompts\n")

    # Setup output
    output_dir = Path(paths_config.get("output_dir", "./results"))
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"realtime_results_{timestamp}.jsonl"

    # Run analysis
    print("🔄 Analyzing prompts...\n")

    try:
        successful, failed, results = analyzer.analyze_prompts(
            prompts=prompts, output_file=output_file, show_progress=not args.no_progress
        )

        # Generate statistics
        if results:
            stats = processor.generate_statistics(results)
            stats_file = output_dir / f"realtime_stats_{timestamp}.json"

            import json

            with open(stats_file, "w") as f:
                json.dump(stats, f, indent=2)

            print(f"\n✅ Analysis complete!")
            print(f"\nResults:")
            print(f"  - Successful: {successful}")
            print(f"  - Failed: {failed}")
            print(f"  - Output: {output_file}")
            print(f"  - Statistics: {stats_file}")

            # Show some stats
            print(f"\nStatistics:")
            print(f"  - NSFW Distribution: {stats['nsfw_distribution']}")
            print(f"  - Top Art Styles: {list(stats['top_art_styles'].keys())[:5]}")

            return 0
        else:
            print("\n❌ No results generated")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        print(f"Partial results saved to: {output_file}")
        return 1
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    args = parse_args()
    exit_code = run_realtime_analysis(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
