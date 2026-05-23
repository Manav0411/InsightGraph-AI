import urllib.request
import json

url = "http://localhost:8000/newsletter/generate-stream"
data = json.dumps({
    "user_id": "default_user",
    "preferred_topics": ["AI Agents"],
    "excluded_topics": ["Cryptocurrency"]
}).encode('utf-8')

req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')
req.add_header('Accept', 'text/event-stream')

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.getcode()}")
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith("data: "):
                try:
                    payload = json.loads(line[6:])
                    print(f"Stage: {payload.get('stage')} - Status: {payload.get('status')} - Error: {payload.get('error', 'None')}")
                except json.JSONDecodeError:
                    print(line)
except Exception as e:
    print(f"Error: {e}")
