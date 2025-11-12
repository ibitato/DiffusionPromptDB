"""
Utility functions for the batch analyzer.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv
import os


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
        log_file: Optional log file path
        log_format: Log message format
        
    Returns:
        Root logger
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Convert level string to logging constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Configure root logger
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        # Create log directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger()


def load_config(config_file: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to config file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_file}\n"
            f"Copy config.yaml.example to config.yaml and configure it."
        )
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    return config


def load_environment():
    """
    Load environment variables from .env file if it exists.
    """
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)


def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (valid: bool, errors: list[str])
    """
    errors = []
    
    # Check required sections
    required_sections = ['aws', 'bedrock', 'batch', 'paths']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required config section: {section}")
    
    # Validate AWS config
    if 'aws' in config:
        aws_config = config['aws']
        if 'region' not in aws_config:
            errors.append("Missing aws.region in config")
    
    # Validate Bedrock config
    if 'bedrock' in config:
        bedrock_config = config['bedrock']
        if 'model_id' not in bedrock_config:
            errors.append("Missing bedrock.model_id in config")
    
    # Validate paths
    if 'paths' in config:
        paths_config = config['paths']
        if 'input_file' not in paths_config:
            errors.append("Missing paths.input_file in config")
        elif not Path(paths_config['input_file']).exists():
            errors.append(f"Input file not found: {paths_config['input_file']}")
    
    return len(errors) == 0, errors


def get_s3_bucket_from_config(config: dict) -> Optional[str]:
    """
    Extract S3 bucket name from config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        S3 bucket name or None
    """
    batch_config = config.get('batch', {})
    
    # Try input S3 URI first
    input_uri = batch_config.get('input_s3_uri')
    if input_uri and input_uri.startswith('s3://'):
        return input_uri.split('/')[2]
    
    # Try output S3 URI
    output_uri = batch_config.get('output_s3_uri')
    if output_uri and output_uri.startswith('s3://'):
        return output_uri.split('/')[2]
    
    # Check environment variable
    bucket = os.environ.get('AWS_S3_BATCH_BUCKET')
    if bucket:
        return bucket
    
    return None


def format_size(num_bytes: int) -> str:
    """
    Format bytes into human-readable string.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format seconds into human-readable duration.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        Stable Diffusion Prompt Batch Analyzer           ║
║                                                          ║
║        Powered by AWS Bedrock & Claude Sonnet           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_cost_estimate(cost_info: dict):
    """
    Print cost estimate in a formatted way.
    
    Args:
        cost_info: Cost information dictionary
    """
    print("\n" + "="*60)
    print("COST ESTIMATE".center(60))
    print("="*60)
    print(f"Number of prompts:       {cost_info['num_prompts']:,}")
    print(f"Total input tokens:      {cost_info['total_input_tokens']:,}")
    print(f"Total output tokens:     {cost_info['total_output_tokens']:,}")
    print("-"*60)
    print(f"Input cost:              ${cost_info['input_cost_usd']:.2f} USD")
    print(f"Output cost:             ${cost_info['output_cost_usd']:.2f} USD")
    print("-"*60)
    print(f"TOTAL COST:              ${cost_info['total_cost_usd']:.2f} USD")
    print(f"Cost per prompt:         ${cost_info['cost_per_prompt_usd']:.4f} USD")
    print("="*60)
    print("\nNote: This is an estimate. Actual costs may vary.")
    print("Batch API includes 50% discount on standard pricing.\n")
