"""
Prompt Analyzer

Main orchestrator for analyzing Stable Diffusion prompts using AWS Bedrock.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from .bedrock_client import BedrockBatchClient
from .batch_processor import BatchProcessor
from .prompt_template import PromptTemplate


logger = logging.getLogger(__name__)


class PromptAnalyzer:
    """Main analyzer for processing prompts through Bedrock."""
    
    def __init__(
        self,
        input_file: str,
        output_dir: str,
        model_id: str,
        aws_profile: Optional[str] = None,
        aws_region: str = "us-east-1",
        batch_size: int = 200,
        max_tokens: int = 2000,
        temperature: float = 0.0
    ):
        """
        Initialize the analyzer.
        
        Args:
            input_file: Path to input JSONL file
            output_dir: Directory for output files
            model_id: Bedrock model ID
            aws_profile: AWS profile name
            aws_region: AWS region
            batch_size: Prompts per batch
            max_tokens: Maximum tokens for responses
            temperature: Sampling temperature
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.model_id = model_id
        self.batch_size = batch_size
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize clients
        self.bedrock_client = BedrockBatchClient(
            profile_name=aws_profile,
            region_name=aws_region
        )
        
        self.processor = BatchProcessor(
            input_file=input_file,
            batch_size=batch_size
        )
        
        logger.info(f"Initialized PromptAnalyzer with model {model_id}")
    
    def verify_setup(self) -> Tuple[bool, List[str]]:
        """
        Verify that everything is set up correctly.
        
        Returns:
            Tuple of (success: bool, messages: List[str])
        """
        messages = []
        all_ok = True
        
        # Check input file
        if not Path(self.input_file).exists():
            messages.append(f"❌ Input file not found: {self.input_file}")
            all_ok = False
        else:
            count = self.processor.count_prompts()
            messages.append(f"✓ Input file found: {count} prompts")
        
        # Check AWS connection
        success, msg = self.bedrock_client.test_connection()
        if success:
            messages.append(f"✓ AWS connection successful")
        else:
            messages.append(f"❌ AWS connection failed: {msg}")
            all_ok = False
        
        # Check model availability
        success, msg = self.bedrock_client.check_model_available(self.model_id)
        if success:
            messages.append(f"✓ Model {self.model_id} is available")
        else:
            messages.append(f"❌ Model check failed: {msg}")
            all_ok = False
        
        # Check output directory
        if self.output_dir.exists():
            messages.append(f"✓ Output directory ready: {self.output_dir}")
        else:
            messages.append(f"❌ Output directory not accessible: {self.output_dir}")
            all_ok = False
        
        return all_ok, messages
    
    def create_batch_requests(
        self,
        prompts: List[Dict]
    ) -> List[Dict]:
        """
        Create batch request format for Bedrock.
        
        Args:
            prompts: List of prompt dicts with 'id' and 'prompt'
            
        Returns:
            List of batch request dicts
        """
        requests = []
        
        for prompt in prompts:
            request = PromptTemplate.generate_batch_request(
                prompt_id=prompt['id'],
                prompt_text=prompt['prompt'],
                model_id=self.model_id,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            requests.append(request)
        
        return requests
    
    def process_batch_results(
        self,
        batch_results: List[Dict],
        original_prompts: Dict[int, str]
    ) -> List[Dict]:
        """
        Process raw batch results into structured format.
        
        Args:
            batch_results: Raw results from Bedrock
            original_prompts: Map of prompt ID to original text
            
        Returns:
            List of structured analysis results
        """
        processed = []
        
        for result in batch_results:
            try:
                record_id = int(result.get('recordId'))
                model_output = result.get('modelOutput', {})
                
                # Extract response content
                content = model_output.get('content', [])
                if content and len(content) > 0:
                    response_text = content[0].get('text', '')
                else:
                    logger.warning(f"No content for record {record_id}")
                    continue
                
                # Parse JSON response
                categories = PromptTemplate.parse_response(response_text)
                
                # Validate structure
                if not PromptTemplate.validate_response_structure(categories):
                    logger.warning(f"Invalid structure for record {record_id}")
                    continue
                
                # Get token usage
                usage = model_output.get('usage', {})
                
                # Build final result
                analysis_result = {
                    'id': record_id,
                    'original_prompt': original_prompts.get(record_id, ''),
                    'categories': categories,
                    'metadata': {
                        'processed_at': datetime.utcnow().isoformat(),
                        'model_used': self.model_id,
                        'tokens_used': {
                            'input': usage.get('inputTokens', 0),
                            'output': usage.get('outputTokens', 0)
                        }
                    }
                }
                
                processed.append(analysis_result)
                
            except Exception as e:
                logger.error(f"Error processing result: {e}")
                continue
        
        return processed
    
    def analyze_prompts(
        self,
        dry_run: bool = False,
        dry_run_count: int = 10,
        resume_from_id: Optional[int] = None,
        s3_bucket: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Analyze prompts using Bedrock Batch API.
        
        Args:
            dry_run: If True, only process dry_run_count prompts
            dry_run_count: Number of prompts for dry run
            resume_from_id: Resume from this prompt ID
            s3_bucket: S3 bucket for batch processing (created if None)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Determine number of prompts to process
            if dry_run:
                max_count = dry_run_count
                logger.info(f"Running in DRY RUN mode with {max_count} prompts")
            else:
                max_count = None
                logger.info("Running in FULL mode")
            
            # Count total prompts
            total_count = self.processor.count_prompts()
            prompts_to_process = min(max_count or total_count, total_count)
            
            # Show cost estimate
            cost_estimate = self.processor.estimate_cost(prompts_to_process)
            logger.info(f"Cost estimate: ${cost_estimate['total_cost_usd']} USD for {prompts_to_process} prompts")
            
            # Generate timestamp for this run
            timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            
            # Determine S3 paths
            if s3_bucket:
                input_s3_uri = f"s3://{s3_bucket}/batch-analyzer/input/{timestamp}/input.jsonl"
                output_s3_uri = f"s3://{s3_bucket}/batch-analyzer/output/{timestamp}/"
            else:
                # Use default bucket naming
                bucket_name = f"bedrock-batch-{timestamp.lower()}"
                logger.warning(f"No S3 bucket specified. You'll need to create: {bucket_name}")
                return False, "S3 bucket must be specified. Please configure s3_bucket in config."
            
            # Read and create batch requests
            logger.info("Reading prompts and creating batch requests...")
            all_prompts = []
            original_prompts = {}
            
            for prompt in self.processor.read_prompts(
                start_id=resume_from_id,
                max_count=max_count
            ):
                all_prompts.append(prompt)
                original_prompts[prompt['id']] = prompt['prompt']
            
            if not all_prompts:
                return False, "No prompts to process"
            
            logger.info(f"Creating batch requests for {len(all_prompts)} prompts...")
            batch_requests = self.create_batch_requests(all_prompts)
            
            # Upload to S3
            logger.info(f"Uploading batch input to {input_s3_uri}...")
            success, msg = self.bedrock_client.upload_batch_input(batch_requests, input_s3_uri)
            if not success:
                return False, f"Failed to upload input: {msg}"
            
            # Create batch job
            job_name = f"prompt-analysis-{timestamp}"
            logger.info(f"Creating batch job: {job_name}...")
            success, job_arn, msg = self.bedrock_client.create_batch_job(
                job_name=job_name,
                model_id=self.model_id,
                input_s3_uri=input_s3_uri,
                output_s3_uri=output_s3_uri
            )
            
            if not success:
                return False, f"Failed to create batch job: {msg}"
            
            logger.info(f"Batch job created: {job_arn}")
            logger.info("Job is now processing. This may take several hours.")
            logger.info(f"Check status with job ARN: {job_arn}")
            
            # Save job info for later retrieval
            job_info_file = self.output_dir / f"job_{timestamp}.json"
            job_info = {
                'job_arn': job_arn,
                'job_name': job_name,
                'timestamp': timestamp,
                'input_s3_uri': input_s3_uri,
                'output_s3_uri': output_s3_uri,
                'model_id': self.model_id,
                'num_prompts': len(all_prompts),
                'cost_estimate': cost_estimate
            }
            
            with open(job_info_file, 'w') as f:
                json.dump(job_info, f, indent=2)
            
            logger.info(f"Job info saved to: {job_info_file}")
            
            return True, f"Batch job started successfully. Job ARN: {job_arn}"
            
        except Exception as e:
            logger.error(f"Error in analyze_prompts: {e}", exc_info=True)
            return False, f"Error: {str(e)}"
    
    def retrieve_results(
        self,
        job_info_file: str
    ) -> Tuple[bool, str]:
        """
        Retrieve results from a completed batch job.
        
        Args:
            job_info_file: Path to job info JSON file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Load job info
            with open(job_info_file) as f:
                job_info = json.load(f)
            
            job_arn = job_info['job_arn']
            output_s3_uri = job_info['output_s3_uri']
            timestamp = job_info['timestamp']
            
            logger.info(f"Checking status of job: {job_arn}")
            
            # Check job status
            success, job_status, msg = self.bedrock_client.get_job_status(job_arn)
            if not success:
                return False, f"Failed to get job status: {msg}"
            
            if job_status['status'] != 'Completed':
                return False, f"Job not completed yet. Status: {job_status['status']}"
            
            # Download results
            logger.info("Downloading results from S3...")
            success, batch_results, msg = self.bedrock_client.download_batch_output(output_s3_uri)
            if not success:
                return False, f"Failed to download results: {msg}"
            
            # Load original prompts
            original_prompts = {}
            for prompt in self.processor.read_prompts():
                original_prompts[prompt['id']] = prompt['prompt']
            
            # Process results
            logger.info("Processing results...")
            processed_results = self.process_batch_results(batch_results, original_prompts)
            
            # Save results
            results_file = self.output_dir / f"analysis_results_{timestamp}.jsonl"
            success = self.processor.save_results(processed_results, results_file)
            
            if not success:
                return False, "Failed to save results"
            
            # Generate statistics
            logger.info("Generating statistics...")
            stats = self.processor.generate_statistics(processed_results)
            stats_file = self.output_dir / f"statistics_{timestamp}.json"
            
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"Results saved to: {results_file}")
            logger.info(f"Statistics saved to: {stats_file}")
            
            return True, f"Successfully retrieved {len(processed_results)} results"
            
        except Exception as e:
            logger.error(f"Error retrieving results: {e}", exc_info=True)
            return False, f"Error: {str(e)}"
