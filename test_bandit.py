
from services.scan_service import scan_project_code

result = scan_project_code(".")

print("Project:", result.get("project"))
print("Python files scanned:", result.get("total_files"))
print("Total security issues:", result.get("total_issues"))

for file_result in result.get("results", []):
    print("\nFile:", file_result["file"])

    for issue in file_result.get("issues", []):
        print("  Severity:", issue["severity"])
        print("  Issue:", issue["title"])
        print("  Line:", issue["line"])
