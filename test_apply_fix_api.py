
import requests

url = "http://127.0.0.1:5000/api/apply-fix"

data = {
    "project_id": "c652e3b5152e425691736c1033e11514",
    "file_name": "test_scan.py",
    "fixed_code": 'message = "updated"\n',
    "confirm_apply": True
}

response = requests.post(url, json=data)

print("Status code:", response.status_code)
print(response.json())
