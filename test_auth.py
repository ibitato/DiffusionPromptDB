import json
import urllib.request
import urllib.error

# Test authentication endpoint
url = "http://localhost:8000/api/v1/auth/login"
data = {
    "username": "admin",
    "password": "admin"
}

try:
    # Convert data to JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    # Make request
    response = urllib.request.urlopen(req)
    
    # Read response
    response_data = json.loads(response.read().decode('utf-8'))
    
    print(f"Status Code: {response.getcode()}")
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    error_body = e.read().decode('utf-8')
    print(f"Error details: {error_body}")
except Exception as e:
    print(f"Error: {e}")
