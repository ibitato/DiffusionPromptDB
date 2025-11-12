#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from core.bedrock_client import BedrockBatchClient

# Find latest job file
results_dir = Path("results")
job_files = list(results_dir.glob("job_*.json"))
if not job_files:
    print("No job files found")
    sys.exit(1)

latest_job = max(job_files, key=lambda p: p.stat().st_mtime)
print(f"Checking job: {latest_job.name}\n")

# Load job info
with open(latest_job) as f:
    job_info = json.load(f)

# Check status
client = BedrockBatchClient(region_name="us-east-1")
success, status, msg = client.get_job_status(job_info["job_arn"])

if success:
    print(f"Job Status: {status['status']}")
    print(f"Model: {status['model_id']}")
    print(f"Submit Time: {status['submit_time']}")
    if "end_time" in status:
        print(f"End Time: {status['end_time']}")
    if "failure_message" in status:
        print(f"Failure: {status['failure_message']}")
else:
    print(f"Error: {msg}")
