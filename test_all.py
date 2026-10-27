
import requests
import zipfile
import io

BASE_URL = "http://127.0.0.1:5000"


def test_api(name, method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{BASE_URL}{endpoint}",
            timeout=15,
            **kwargs
        )

        passed = 200 <= response.status_code < 300

        print(f"\n{'PASS' if passed else 'FAIL'}: {name}")
        print(f"Status Code: {response.status_code}")

        try:
            print(response.json())
        except ValueError:
            print(response.text[:300])

        return passed

    except requests.RequestException as error:
        print(f"\nFAIL: {name}")
        print(f"Error: {error}")
        return False


def main():
    print("=" * 45)
    print("       SECURECODE AI - API TESTS")
    print("=" * 45)

    results = []

    # 1. Backend status
    results.append(
        test_api("Backend Status", "GET", "/")
    )

    # 2. Scan history
    results.append(
        test_api("Scan History", "GET", "/api/history")
    )

    # 3. Existing saved report
    project_id = "c652e3b5152e425691736c1033e11514"

    results.append(
        test_api(
            "Report API",
            "GET",
            f"/api/report/{project_id}"
        )
    )

    # 4. Fix suggestion API
    results.append(
        test_api(
            "Fix Suggestion API",
            "POST",
            "/api/fix-suggestion",
            json={
                "project_id": project_id,
                "file_name": "test_scan.py",
                "issue_line": 6,
                "test_id": "B602"
            }
        )
    )

    # 5. Upload API using a harmless sample Python file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr(
            "sample.py",
            'message = "Hello SecureCode AI"\nprint(message)\n'
        )

    zip_buffer.seek(0)

    results.append(
        test_api(
            "ZIP Upload and Scan API",
            "POST",
            "/api/upload",
            files={
                "file": (
                    "securecode_test.zip",
                    zip_buffer,
                    "application/zip"
                )
            }
        )
    )

    # 6. Apply Fix confirmation protection (no code is changed)
    results.append(
        test_api(
            "Apply Fix Confirmation Protection",
            "POST",
            "/api/apply-fix",
            json={
                "project_id": project_id,
                "file_name": "test_scan.py",
                "fixed_code": 'message = "test"\n',
                "confirm_apply": False
            }
        )
        is False
    )

    passed = sum(results)
    failed = len(results) - passed

    print("\n" + "=" * 45)
    print("             FINAL SUMMARY")
    print("=" * 45)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\nAll API checks passed!")
    else:
        print("\nSome checks need attention. Review the output above.")


if __name__ == "__main__":
    main()
