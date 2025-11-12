"""
AWS Bedrock Batch Client

This module provides a client for interacting with AWS Bedrock's Batch Inference API.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, BotoCoreError


logger = logging.getLogger(__name__)


class BedrockBatchClient:
    """Client for AWS Bedrock Batch Inference API."""
    
    def __init__(self, profile_name: Optional[str] = None, region_name: str = "us-east-1"):
        """
        Initialize Bedrock Batch client.
        
        Args:
            profile_name: AWS profile name (None uses default credentials)
            region_name: AWS region where Bedrock is available
        """
        self.region_name = region_name
        self.profile_name = profile_name
        
        # Create session
        if profile_name:
            session = boto3.Session(profile_name=profile_name, region_name=region_name)
        else:
            session = boto3.Session(region_name=region_name)
        
        # Create clients
        self.bedrock_client = session.client('bedrock')
        self.s3_client = session.client('s3')
        
        logger.info(f"Initialized Bedrock client in region {region_name}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test AWS credentials and Bedrock access.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try to list foundation models
            response = self.bedrock_client.list_foundation_models()
            models = response.get('modelSummaries', [])
            
            if models:
                return True, f"Successfully connected. Found {len(models)} models available."
            else:
                return False, "Connected but no models found. Check Bedrock access."
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                return False, "Access denied. Check IAM permissions for Bedrock."
            else:
                return False, f"AWS Error: {error_code} - {e.response['Error']['Message']}"
        except BotoCoreError as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def check_model_available(self, model_id: str) -> Tuple[bool, str]:
        """
        Check if a specific model is available.
        
        Args:
            model_id: Bedrock model ID
            
        Returns:
            Tuple of (available: bool, message: str)
        """
        try:
            response = self.bedrock_client.get_foundation_model(modelIdentifier=model_id)
            model_info = response.get('modelDetails', {})
            
            return True, f"Model {model_id} is available. Status: {model_info.get('modelLifecycle', {}).get('status', 'unknown')}"
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False, f"Model {model_id} not found. Check model ID and region."
            else:
                return False, f"Error checking model: {e.response['Error']['Message']}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def upload_batch_input(self, requests: List[Dict], s3_uri: str) -> Tuple[bool, str]:
        """
        Upload batch input file to S3.
        
        Args:
            requests: List of batch request dictionaries
            s3_uri: S3 URI for input file (s3://bucket/key)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Parse S3 URI
            if not s3_uri.startswith('s3://'):
                return False, "S3 URI must start with 's3://'"
            
            parts = s3_uri[5:].split('/', 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else 'batch_input.jsonl'
            
            # Create JSONL content
            jsonl_content = '\n'.join(json.dumps(req) for req in requests)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=jsonl_content.encode('utf-8'),
                ContentType='application/jsonl'
            )
            
            logger.info(f"Uploaded {len(requests)} requests to {s3_uri}")
            return True, f"Successfully uploaded {len(requests)} requests"
            
        except ClientError as e:
            return False, f"S3 upload error: {e.response['Error']['Message']}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def create_batch_job(
        self,
        job_name: str,
        model_id: str,
        input_s3_uri: str,
        output_s3_uri: str,
        role_arn: Optional[str] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Create a Bedrock batch inference job.
        
        Args:
            job_name: Name for the batch job
            model_id: Bedrock model ID
            input_s3_uri: S3 URI of input JSONL file
            output_s3_uri: S3 URI prefix for output
            role_arn: IAM role ARN (if None, tries to get account ID and use default role)
            
        Returns:
            Tuple of (success: bool, job_arn: Optional[str], message: str)
        """
        try:
            # If no role_arn provided, try to construct one using account ID
            if not role_arn:
                try:
                    sts = boto3.client('sts')
                    account_id = sts.get_caller_identity()['Account']
                    role_arn = f"arn:aws:iam::{account_id}:role/BedrockBatchAnalyzerRole"
                    logger.info(f"Using default role: {role_arn}")
                except Exception as e:
                    logger.warning(f"Could not get account ID: {e}")
            
            # Prepare request
            request_params = {
                'jobName': job_name,
                'modelId': model_id,
                'inputDataConfig': {
                    's3InputDataConfig': {
                        's3Uri': input_s3_uri
                    }
                },
                'outputDataConfig': {
                    's3OutputDataConfig': {
                        's3Uri': output_s3_uri
                    }
                }
            }
            
            # Add role ARN - it's required
            if role_arn:
                request_params['roleArn'] = role_arn
            else:
                return False, None, "IAM role ARN is required for batch jobs"
            
            # Create batch job
            response = self.bedrock_client.create_model_invocation_job(**request_params)
            
            job_arn = response['jobArn']
            logger.info(f"Created batch job: {job_arn}")
            
            return True, job_arn, f"Batch job created successfully"
            
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            return False, None, f"Failed to create batch job: {error_msg}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def get_job_status(self, job_arn: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Get status of a batch job.
        
        Args:
            job_arn: ARN of the batch job
            
        Returns:
            Tuple of (success: bool, job_info: Optional[Dict], message: str)
        """
        try:
            response = self.bedrock_client.get_model_invocation_job(jobIdentifier=job_arn)
            
            job_info = {
                'status': response['status'],
                'job_name': response['jobName'],
                'model_id': response['modelId'],
                'submit_time': response['submitTime'],
                'input_config': response['inputDataConfig'],
                'output_config': response['outputDataConfig']
            }
            
            # Add end time if completed
            if 'endTime' in response:
                job_info['end_time'] = response['endTime']
            
            # Add failure reason if failed
            if 'failureMessage' in response:
                job_info['failure_message'] = response['failureMessage']
            
            return True, job_info, f"Status: {response['status']}"
            
        except ClientError as e:
            return False, None, f"Error getting job status: {e.response['Error']['Message']}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def wait_for_job_completion(
        self,
        job_arn: str,
        check_interval: int = 300,
        timeout: int = 86400
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Wait for batch job to complete.
        
        Args:
            job_arn: ARN of the batch job
            check_interval: Seconds between status checks (default: 300 = 5 minutes)
            timeout: Maximum time to wait in seconds (default: 86400 = 24 hours)
            
        Returns:
            Tuple of (success: bool, job_info: Optional[Dict], message: str)
        """
        start_time = time.time()
        
        while True:
            # Check if timeout exceeded
            elapsed = time.time() - start_time
            if elapsed > timeout:
                return False, None, f"Timeout after {elapsed:.0f} seconds"
            
            # Get job status
            success, job_info, msg = self.get_job_status(job_arn)
            
            if not success:
                return False, None, msg
            
            status = job_info['status']
            
            if status == 'Completed':
                logger.info(f"Job completed successfully")
                return True, job_info, "Job completed successfully"
            
            elif status == 'Failed':
                failure_msg = job_info.get('failure_message', 'Unknown error')
                logger.error(f"Job failed: {failure_msg}")
                return False, job_info, f"Job failed: {failure_msg}"
            
            elif status in ['InProgress', 'Submitted', 'Validating']:
                logger.info(f"Job status: {status}. Waiting {check_interval}s...")
                time.sleep(check_interval)
            
            else:
                logger.warning(f"Unknown job status: {status}")
                time.sleep(check_interval)
    
    def download_batch_output(self, output_s3_uri: str) -> Tuple[bool, Optional[List[Dict]], str]:
        """
        Download and parse batch output from S3.
        
        Args:
            output_s3_uri: S3 URI of output file
            
        Returns:
            Tuple of (success: bool, results: Optional[List[Dict]], message: str)
        """
        try:
            # Parse S3 URI
            if not output_s3_uri.startswith('s3://'):
                return False, None, "Output URI must start with 's3://'"
            
            parts = output_s3_uri[5:].split('/', 1)
            bucket = parts[0]
            prefix = parts[1] if len(parts) > 1 else ''
            
            # List objects in the output location
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            
            if 'Contents' not in response:
                return False, None, "No output files found"
            
            # Download and parse all output files
            results = []
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('.jsonl') or key.endswith('.jsonl.out'):
                    logger.info(f"Downloading {key}")
                    
                    response = self.s3_client.get_object(Bucket=bucket, Key=key)
                    content = response['Body'].read().decode('utf-8')
                    
                    # Parse JSONL
                    for line in content.strip().split('\n'):
                        if line.strip():
                            results.append(json.loads(line))
            
            logger.info(f"Downloaded {len(results)} results")
            return True, results, f"Successfully downloaded {len(results)} results"
            
        except ClientError as e:
            return False, None, f"S3 download error: {e.response['Error']['Message']}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def list_batch_jobs(self, max_results: int = 10) -> Tuple[bool, Optional[List[Dict]], str]:
        """
        List recent batch jobs.
        
        Args:
            max_results: Maximum number of jobs to return
            
        Returns:
            Tuple of (success: bool, jobs: Optional[List[Dict]], message: str)
        """
        try:
            response = self.bedrock_client.list_model_invocation_jobs(
                maxResults=max_results,
                sortBy='SubmitTime',
                sortOrder='Descending'
            )
            
            jobs = response.get('invocationJobSummaries', [])
            return True, jobs, f"Found {len(jobs)} jobs"
            
        except ClientError as e:
            return False, None, f"Error listing jobs: {e.response['Error']['Message']}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
