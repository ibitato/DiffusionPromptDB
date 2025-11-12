"""
Batch Processor

This module handles reading prompts from JSONL files, creating batch requests,
and processing results.
"""

import json
import logging
from typing import Dict, List, Iterator, Optional
from pathlib import Path
import jsonlines
from datetime import datetime


logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processor for handling batch operations on prompt data."""

    def __init__(self, input_file: str, batch_size: int = 200):
        """
        Initialize batch processor.

        Args:
            input_file: Path to input JSONL file
            batch_size: Number of prompts per batch
        """
        self.input_file = Path(input_file)
        self.batch_size = batch_size

        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        logger.info(f"Initialized BatchProcessor with file: {input_file}")

    def count_prompts(self) -> int:
        """
        Count total number of prompts in input file.

        Returns:
            int: Total prompt count
        """
        count = 0
        try:
            with jsonlines.open(self.input_file) as reader:
                for _ in reader:
                    count += 1
            return count
        except Exception as e:
            logger.error(f"Error counting prompts: {e}")
            return 0

    def read_prompts(
        self, start_id: Optional[int] = None, max_count: Optional[int] = None
    ) -> Iterator[Dict]:
        """
        Read prompts from input file.

        Args:
            start_id: Start from this prompt ID (inclusive)
            max_count: Maximum number of prompts to read

        Yields:
            Dict with 'id' and 'prompt' fields
        """
        count = 0

        try:
            with jsonlines.open(self.input_file) as reader:
                for obj in reader:
                    # Validate required fields
                    if "id" not in obj or "prompt" not in obj:
                        logger.warning(f"Skipping invalid entry: {obj}")
                        continue

                    # Skip if before start_id
                    if start_id is not None and obj["id"] < start_id:
                        continue

                    yield obj

                    count += 1
                    if max_count is not None and count >= max_count:
                        break

        except Exception as e:
            logger.error(f"Error reading prompts: {e}")
            raise

    def create_batches(
        self, start_id: Optional[int] = None, max_count: Optional[int] = None
    ) -> Iterator[List[Dict]]:
        """
        Create batches of prompts.

        Args:
            start_id: Start from this prompt ID (inclusive)
            max_count: Maximum number of prompts to process

        Yields:
            List of prompt dictionaries (batch)
        """
        batch = []

        for prompt in self.read_prompts(start_id, max_count):
            batch.append(prompt)

            if len(batch) >= self.batch_size:
                yield batch
                batch = []

        # Yield remaining prompts
        if batch:
            yield batch

    def save_results(
        self, results: List[Dict], output_file: Path, append: bool = False
    ) -> bool:
        """
        Save analysis results to file.

        Args:
            results: List of analysis results
            output_file: Output file path
            append: If True, append to existing file

        Returns:
            bool: Success status
        """
        try:
            # Create output directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)

            mode = "a" if append else "w"

            with jsonlines.open(output_file, mode=mode) as writer:
                for result in results:
                    writer.write(result)

            logger.info(f"Saved {len(results)} results to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

    def load_existing_results(self, results_file: Path) -> Dict[int, Dict]:
        """
        Load existing results from file.

        Args:
            results_file: Path to existing results file

        Returns:
            Dict mapping prompt ID to result
        """
        results = {}

        if not results_file.exists():
            return results

        try:
            with jsonlines.open(results_file) as reader:
                for obj in reader:
                    if "id" in obj:
                        results[obj["id"]] = obj

            logger.info(f"Loaded {len(results)} existing results")
            return results

        except Exception as e:
            logger.error(f"Error loading existing results: {e}")
            return {}

    def get_unprocessed_ids(self, results_file: Path) -> set:
        """
        Get set of prompt IDs that haven't been processed yet.

        Args:
            results_file: Path to results file

        Returns:
            set: Set of unprocessed prompt IDs
        """
        # Get all prompt IDs
        all_ids = set()
        for prompt in self.read_prompts():
            all_ids.add(prompt["id"])

        # Get processed IDs
        existing_results = self.load_existing_results(results_file)
        processed_ids = set(existing_results.keys())

        # Return difference
        unprocessed = all_ids - processed_ids
        logger.info(f"Found {len(unprocessed)} unprocessed prompts")

        return unprocessed

    def estimate_cost(
        self,
        num_prompts: int,
        avg_input_tokens: int = 300,
        avg_output_tokens: int = 800,
        input_cost_per_million: float = 3.0,
        output_cost_per_million: float = 15.0,
        batch_discount: float = 0.5,
    ) -> Dict[str, float]:
        """
        Estimate processing cost.

        Args:
            num_prompts: Number of prompts to process
            avg_input_tokens: Average input tokens per prompt
            avg_output_tokens: Average output tokens per prompt
            input_cost_per_million: Cost per million input tokens
            output_cost_per_million: Cost per million output tokens
            batch_discount: Batch API discount (0.5 = 50% off)

        Returns:
            Dict with cost breakdown
        """
        total_input_tokens = num_prompts * avg_input_tokens
        total_output_tokens = num_prompts * avg_output_tokens

        # Calculate base costs
        input_cost = (total_input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (total_output_tokens / 1_000_000) * output_cost_per_million

        # Apply batch discount
        discounted_input = input_cost * batch_discount
        discounted_output = output_cost * batch_discount

        total_cost = discounted_input + discounted_output

        return {
            "num_prompts": num_prompts,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "input_cost_usd": round(discounted_input, 2),
            "output_cost_usd": round(discounted_output, 2),
            "total_cost_usd": round(total_cost, 2),
            "cost_per_prompt_usd": (
                round(total_cost / num_prompts, 4) if num_prompts > 0 else 0
            ),
        }

    def generate_statistics(self, results: List[Dict]) -> Dict:
        """
        Generate statistics from analysis results.

        Args:
            results: List of analysis results

        Returns:
            Dict with statistics
        """
        stats = {
            "total_prompts": len(results),
            "timestamp": datetime.utcnow().isoformat(),
            "nsfw_distribution": {"safe": 0, "suggestive": 0, "explicit": 0},
            "top_art_styles": {},
            "character_counts": {},
            "common_tags": {},
        }

        for result in results:
            try:
                categories = result.get("categories", {})

                # NSFW distribution
                nsfw_level = categories.get("nsfw_content", {}).get("level", "unknown")
                if nsfw_level in stats["nsfw_distribution"]:
                    stats["nsfw_distribution"][nsfw_level] += 1

                # Art styles
                art_style = categories.get("art_style", {}).get(
                    "primary_style", "unknown"
                )
                stats["top_art_styles"][art_style] = (
                    stats["top_art_styles"].get(art_style, 0) + 1
                )

                # Character counts
                char_count = categories.get("character", {}).get("count", 0)
                stats["character_counts"][str(char_count)] = (
                    stats["character_counts"].get(str(char_count), 0) + 1
                )

                # Common tags
                main_tags = categories.get("main_tags", [])
                for tag in main_tags[:5]:  # Top 5 tags per prompt
                    stats["common_tags"][tag] = stats["common_tags"].get(tag, 0) + 1

            except Exception as e:
                logger.warning(f"Error processing result for stats: {e}")
                continue

        # Sort and limit
        stats["top_art_styles"] = dict(
            sorted(stats["top_art_styles"].items(), key=lambda x: x[1], reverse=True)[
                :10
            ]
        )
        stats["common_tags"] = dict(
            sorted(stats["common_tags"].items(), key=lambda x: x[1], reverse=True)[:50]
        )

        return stats
