"""
Real-time Prompt Analyzer

Analyze prompts in real-time using AWS Bedrock's standard invoke API.
Uses Claude 3.5 Haiku for fast, cost-effective processing.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import time

from .prompt_template import PromptTemplate


logger = logging.getLogger(__name__)


class RealtimeAnalyzer:
    """Real-time analyzer using Bedrock's standard invoke API."""
    
    def __init__(
        self,
        aws_profile: Optional[str] = None,
        aws_region: str = "us-east-1",
        model_id: str = "anthropic.claude-3-5-haiku-20241022-v1:0",
        max_tokens: int = 2000,
        temperature: float = 0.0
    ):
        """
        Initialize real-time analyzer.
        
        Args:
            aws_profile: AWS profile name
            aws_region: AWS region
            model_id: Bedrock model ID (default: Claude 3.5 Haiku)
            max_tokens: Maximum tokens for responses
            temperature: Sampling temperature
        """
        import boto3
        
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Create session
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        else:
            session = boto3.Session(region_name=aws_region)
        
        # Create Bedrock Runtime client for invoke
        self.bedrock_runtime = session.client('bedrock-runtime', region_name=aws_region)
        
        logger.info(f"Initialized RealtimeAnalyzer with model {model_id}")
    
    def analyze_prompt(
        self,
        prompt_id: int,
        prompt_text: str
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Analyze a single prompt in real-time.
        
        Args:
            prompt_id: Prompt ID
            prompt_text: Prompt text to analyze
            
        Returns:
            Tuple of (success: bool, result: Optional[Dict], message: str)
        """
        try:
            start_time = time.time()
            
            # Generate analysis request
            analysis_request = PromptTemplate.generate_analysis_prompt(prompt_text)
            
            # Prepare request body for Bedrock Runtime
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": analysis_request["system"],
                "messages": analysis_request["messages"]
            }
            
            # Determine if using inference profile or direct model ID
            # Inference profiles start with region prefix (us., global., eu.)
            if self.model_id.startswith(('us.', 'global.', 'eu.', 'ap.', 'ca.')):
                # Using inference profile - use modelId parameter
                response = self.bedrock_runtime.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
            else:
                # Direct model ID - try standard invoke first
                response = self.bedrock_runtime.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content
            content = response_body.get('content', [])
            if not content:
                return False, None, "No content in response"
            
            response_text = content[0].get('text', '')
            
            # Parse JSON response
            categories = PromptTemplate.parse_response(response_text)
            
            # Validate structure
            if not PromptTemplate.validate_response_structure(categories):
                return False, None, "Invalid response structure"
            
            # Get token usage
            usage = response_body.get('usage', {})
            processing_time = int((time.time() - start_time) * 1000)
            
            # Build result
            result = {
                'id': prompt_id,
                'original_prompt': prompt_text,
                'categories': categories,
                'metadata': {
                    'processed_at': datetime.utcnow().isoformat(),
                    'model_used': self.model_id,
                    'processing_time_ms': processing_time,
                    'tokens_used': {
                        'input': usage.get('input_tokens', 0),
                        'output': usage.get('output_tokens', 0)
                    }
                }
            }
            
            return True, result, "Success"
            
        except Exception as e:
            logger.error(f"Error analyzing prompt {prompt_id}: {e}")
            return False, None, str(e)
    
    def analyze_prompts(
        self,
        prompts: List[Dict],
        output_file: Path,
        show_progress: bool = True
    ) -> Tuple[int, int, List[Dict]]:
        """
        Analyze multiple prompts in real-time.
        
        Args:
            prompts: List of prompt dicts with 'id' and 'prompt'
            output_file: Output file path for results
            show_progress: Show progress bar
            
        Returns:
            Tuple of (successful: int, failed: int, results: List[Dict])
        """
        results = []
        successful = 0
        failed = 0
        
        # Create output directory
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Process prompts with progress bar
        iterator = tqdm(prompts, desc="Analyzing prompts", disable=not show_progress)
        
        for prompt in iterator:
            success, result, msg = self.analyze_prompt(prompt['id'], prompt['prompt'])
            
            if success and result:
                results.append(result)
                successful += 1
                
                # Save incrementally
                self._save_result(result, output_file, append=(successful > 1))
            else:
                failed += 1
                logger.warning(f"Failed to analyze prompt {prompt['id']}: {msg}")
            
            # Update progress bar
            if show_progress:
                iterator.set_postfix({
                    'success': successful,
                    'failed': failed
                })
            
            # Small delay to avoid rate limits
            time.sleep(0.1)
        
        logger.info(f"Analysis complete: {successful} successful, {failed} failed")
        return successful, failed, results
    
    def _save_result(self, result: Dict, output_file: Path, append: bool = False):
        """
        Save a single result to file.
        
        Args:
            result: Analysis result
            output_file: Output file path
            append: Append to file or create new
        """
        import jsonlines
        
        mode = 'a' if append else 'w'
        with jsonlines.open(output_file, mode=mode) as writer:
            writer.write(result)
    
    def estimate_cost(
        self,
        num_prompts: int,
        avg_input_tokens: int = 300,
        avg_output_tokens: int = 800
    ) -> Dict[str, float]:
        """
        Estimate processing cost for Haiku.
        
        Claude 3.5 Haiku pricing:
        - Input: $1.00 per million tokens
        - Output: $5.00 per million tokens
        
        Args:
            num_prompts: Number of prompts
            avg_input_tokens: Avg input tokens per prompt
            avg_output_tokens: Avg output tokens per prompt
            
        Returns:
            Cost breakdown
        """
        total_input_tokens = num_prompts * avg_input_tokens
        total_output_tokens = num_prompts * avg_output_tokens
        
        # Haiku pricing (no batch discount since it's real-time)
        input_cost = (total_input_tokens / 1_000_000) * 1.0
        output_cost = (total_output_tokens / 1_000_000) * 5.0
        
        total_cost = input_cost + output_cost
        
        return {
            'num_prompts': num_prompts,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'input_cost_usd': round(input_cost, 2),
            'output_cost_usd': round(output_cost, 2),
            'total_cost_usd': round(total_cost, 2),
            'cost_per_prompt_usd': round(total_cost / num_prompts, 4) if num_prompts > 0 else 0
        }
