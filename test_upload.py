
import requests

url = "http://127.0.0.1:5000/api/upload"

with open("test_scan.zip", "rb") as zip_file:
    response = requests.post(
        url,
      files={"file": ("test_scan.zip", zip_file, "application/zip")}
    )

print("Status code:", response.status_code)
print(response.text)
