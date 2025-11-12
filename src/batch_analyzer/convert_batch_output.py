#!/usr/bin/env python3
"""
Convert AWS Bedrock Batch Output to Import Format

Converts the batch job output format to the format expected by import_to_db.py
"""

import json
import jsonlines
import sys
from pathlib import Path
from datetime import datetime


def extract_prompt_from_batch_line(batch_line: dict, prompt_id: int) -> dict:
    """
    Extract and convert a single batch output line to import format.

    Args:
        batch_line: Raw batch output line
        prompt_id: Sequential ID to assign

    Returns:
        Converted dict in import format
    """
    # Extract original prompt from model input
    messages = batch_line["modelInput"]["messages"]
    full_input = messages[0]["content"]

    # Find the original prompt text (after "PROMPT TO ANALYZE:")
    prompt_start = full_input.find("PROMPT TO ANALYZE:\n\n") + len(
        "PROMPT TO ANALYZE:\n\n"
    )
    prompt_end = full_input.find("\n\nREQUIRED OUTPUT SCHEMA:")
    original_prompt = full_input[prompt_start:prompt_end].strip()

    # Extract analysis from model output
    model_output = batch_line["modelOutput"]
    analysis_json_str = model_output["content"][0]["text"]

    # Parse the analysis JSON
    try:
        categories = json.loads(analysis_json_str)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON for prompt {prompt_id}: {e}")
        return None

    # Build result in expected format
    result = {
        "id": prompt_id,
        "original_prompt": original_prompt,
        "categories": categories,
        "metadata": {
            "processed_at": datetime.utcnow().isoformat(),
            "model_used": model_output.get("model", "claude-3-5-sonnet-20240620"),
            "tokens_used": {
                "input": model_output.get("usage", {}).get("input_tokens", 0),
                "output": model_output.get("usage", {}).get("output_tokens", 0),
            },
            "record_id": batch_line.get("recordId"),
        },
    }

    return result


def convert_batch_output(input_file: str, output_file: str):
    """
    Convert entire batch output file to import format.

    Args:
        input_file: Raw batch output JSONL
        output_file: Converted JSONL for import
    """
    print(f"Converting: {input_file}")
    print(f"Output to: {output_file}")
    print()

    converted = 0
    errors = 0

    with jsonlines.open(input_file) as reader, jsonlines.open(
        output_file, mode="w"
    ) as writer:
        for idx, batch_line in enumerate(reader, start=1):
            try:
                result = extract_prompt_from_batch_line(batch_line, idx)
                if result:
                    writer.write(result)
                    converted += 1
                    if converted % 100 == 0:
                        print(f"Converted {converted} prompts...", end="\r")
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"\nError converting line {idx}: {e}")

    print(f"\n✓ Conversion complete: {converted} successful, {errors} failed")
    return converted, errors


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert batch output to import format"
    )
    parser.add_argument("input_file", help="Batch output JSONL file")
    parser.add_argument("--output", help="Output file (default: converted_<input>)")

    args = parser.parse_args()

    print("=" * 70)
    print("Batch Output Converter")
    print("=" * 70)
    print()

    # Check if file exists
    if not Path(args.input_file).exists():
        print(f"❌ File not found: {args.input_file}")
        return 1

    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input_file)
        output_file = input_path.parent / f"converted_{input_path.name}"

    # Convert
    converted, errors = convert_batch_output(args.input_file, str(output_file))

    if converted > 0:
        print(f"\n✅ Converted file ready: {output_file}")
        print(
            f"   Use with: python import_to_db.py {output_file} --db prompts_catalog.db --stats"
        )

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
