import boto3

client = boto3.client('bedrock', region_name='us-east-1')
profiles = client.list_inference_profiles()

print("Available Inference Profiles:\n")
for p in profiles.get('inferenceProfileSummaries', []):
    name = p.get('inferenceProfileName', '')
    if 'claude' in name.lower():
        profile_id = p.get('inferenceProfileId', '')
        models = p.get('models', [])
        model_id = models[0].get('modelId', '') if models else 'N/A'
        print(f"Name: {name}")
        print(f"ID: {profile_id}")
        print(f"Model: {model_id}")
        print()
