
import json
import subprocess
import sys
from pathlib import Path


def scan_python_file(file_path):
    file_path = Path(file_path)

    if not file_path.is_file() or file_path.suffix != ".py":
        return {
            "error": "A valid Python file is required."
        }

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bandit",
                "-f",
                "json",
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode not in (0, 1):
            return {
                "error": "Bandit scan failed.",
                "details": result.stderr[:1000]
            }

        report = json.loads(result.stdout or "{}")

        issues = []

        for issue in report.get("results", []):
            issues.append({
                "severity": issue.get("issue_severity", "UNKNOWN"),
                "confidence": issue.get("issue_confidence", "UNKNOWN"),
                "test_id": issue.get("test_id", ""),
                "title": issue.get("issue_text", ""),
                "file": issue.get("filename", ""),
                "line": issue.get("line_number", 0)
            })

        return {
            "file": str(file_path),
            "total_issues": len(issues),
            "issues": issues
        }

    except subprocess.TimeoutExpired:
        return {"error": "Scan timed out."}

    except (OSError, json.JSONDecodeError) as error:
        return {
            "error": "Could not complete the scan.",
            "details": str(error)
        }
