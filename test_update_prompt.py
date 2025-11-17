import json
import urllib.request
import urllib.error
import os

from src.api.config import settings

# First login to get token
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {
    "username": "admin",
    "password": "REDACTED_PASSWORD"
}

try:
    # Login
    json_data = json.dumps(login_data).encode('utf-8')
    req = urllib.request.Request(login_url, data=json_data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req)
    auth_response = json.loads(response.read().decode('utf-8'))
    token = auth_response['access_token']
    print(f"Token obtained: {token[:50]}...")
    
    # Get prompt #10384 (uses API key)
    prompt_id = 10384
    api_key = os.getenv("API_TEST_KEY", settings.api_keys[0])
    get_url = f"http://localhost:8000/api/v1/prompts/{prompt_id}"
    req = urllib.request.Request(get_url, headers={'X-API-Key': api_key})
    response = urllib.request.urlopen(req)
    prompt_data = json.loads(response.read().decode('utf-8'))
    print(f"\nOriginal Prompt #{prompt_id}:")
    print(f"  Text: {prompt_data.get('text', '')[:50]}...")
    print(f"  Tags: {prompt_data.get('tags', '')}")
    print(f"  Art Style: {prompt_data.get('art_style', '')}")
    print(f"  Category: {prompt_data.get('category', '')}")
    
    # Update prompt - add tag (uses JWT token)
    update_url = f"http://localhost:8000/api/v1/prompts/{prompt_id}"
    current_tags = prompt_data.get('tags', '')
    new_tags = f"ll, {current_tags}" if current_tags else "ll"
    
    # Send only the fields we want to update
    update_data = {
        "tags": new_tags,
        "text": prompt_data.get('text', ''),  # Keep existing text
        "art_style": prompt_data.get('art_style', ''),  # Keep existing art_style
    }
    
    print(f"\nUpdating with new tags: {new_tags}")
    
    json_data = json.dumps(update_data).encode('utf-8')
    req = urllib.request.Request(
        update_url, 
        data=json_data, 
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        method='PUT'
    )
    response = urllib.request.urlopen(req)
    updated_prompt = json.loads(response.read().decode('utf-8'))
    
    print(f"\nUpdated Prompt #{prompt_id}:")
    print(f"  Text: {updated_prompt.get('text', '')[:50]}...")
    print(f"  Tags: {updated_prompt.get('tags', '')}")
    print(f"  Art Style: {updated_prompt.get('art_style', '')}")
    
    # Verify the update by getting the prompt again (uses API key)
    req = urllib.request.Request(get_url, headers={'X-API-Key': api_key})
    response = urllib.request.urlopen(req)
    verified_prompt = json.loads(response.read().decode('utf-8'))
    
    print(f"\nVerification - Getting prompt again:")
    print(f"  Tags: {verified_prompt.get('tags', '')}")
    
    if 'll' in str(verified_prompt.get('tags', '')):
        print("\n✅ SUCCESS: Tags were updated correctly!")
    else:
        print("\n❌ ERROR: Tags were not saved!")
    
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    error_body = e.read().decode('utf-8')
    print(f"Error details: {error_body}")
except Exception as e:
    print(f"Error: {e}")
