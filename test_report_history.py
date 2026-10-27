
import requests

BASE_URL = "http://127.0.0.1:5000"

project_id = "c652e3b5152e425691736c1033e11514"

print("\n--- Testing Scan Report API ---")

report_response = requests.get(
    f"{BASE_URL}/api/report/{project_id}"
)

print("Report status:", report_response.status_code)
print(report_response.json())


print("\n--- Testing Scan History API ---")

history_response = requests.get(
    f"{BASE_URL}/api/history"
)

print("History status:", history_response.status_code)
print(history_response.json())
