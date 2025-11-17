import json
import urllib.request
import urllib.error
import os

from src.api.config import settings

# Get prompt #10384
prompt_id = 10384
api_key = os.getenv("API_TEST_KEY", settings.api_keys[0])
url = f"http://localhost:8000/api/v1/prompts/{prompt_id}"

try:
    req = urllib.request.Request(url, headers={'X-API-Key': api_key})
    response = urllib.request.urlopen(req)
    prompt_data = json.loads(response.read().decode('utf-8'))
    
    print(f"Prompt #{prompt_id}")
    print("=" * 50)
    print(f"Tags: {prompt_data.get('tags', 'No tiene tags')}")
    print(f"Art Style: {prompt_data.get('art_style', 'No especificado')}")
    print(f"Category: {prompt_data.get('category', 'No especificado')}")
    
    if prompt_data.get('tags'):
        print("\nTags individuales:")
        tags_list = [tag.strip() for tag in prompt_data.get('tags', '').split(',')]
        for i, tag in enumerate(tags_list, 1):
            print(f"  {i}. {tag}")
    
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    error_body = e.read().decode('utf-8')
    print(f"Error details: {error_body}")
except Exception as e:
    print(f"Error: {e}")
