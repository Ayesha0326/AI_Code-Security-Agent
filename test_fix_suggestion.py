
import requests

url = "http://127.0.0.1:5000/api/fix-suggestion"

data = {
    "project_id": "c652e3b5152e425691736c1033e11514",
    "file_name": "test_scan.py",
    "issue_line": 6,
    "test_id": "B602"
}

response = requests.post(url, json=data)

print("Status code:", response.status_code)
print(response.json())
