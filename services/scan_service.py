
from pathlib import Path

from scanner.bandit_scanner import scan_python_file
from scanner.secret_scanner import scan_secrets
from autofix.fix_engine import suggest_fix


SKIP_FOLDERS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "node_modules"
}


def scan_project_code(project_path):
    project_path = Path(project_path).resolve()

    if not project_path.is_dir():
        return {
            "error": "Project folder not found.",
            "total_files": 0,
            "total_issues": 0,
            "severity_counts": {
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            },
            "results": []
        }

    python_files = [
        path
        for path in project_path.rglob("*.py")
        if not any(part in SKIP_FOLDERS for part in path.parts)
    ]

    results = []
    total_issues = 0

    severity_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for file_path in python_files:
        relative_path = str(file_path.relative_to(project_path))

        bandit_result = scan_python_file(file_path)
        secret_result = scan_secrets(file_path)

        if "error" in bandit_result:
            results.append({
                "file": relative_path,
                "total_issues": 0,
                "issues": [],
                "error": bandit_result["error"]
            })
            continue

        issues = list(bandit_result.get("issues", []))

        # Record password lines already reported by Bandit.
        bandit_password_lines = {
            issue.get("line")
            for issue in issues
            if issue.get("test_id") == "B105"
        }

        if "error" not in secret_result:
            for secret in secret_result.get("secrets", []):
                secret_line = secret.get("line", 0)

                # Avoid reporting the same password twice.
                if secret_line in bandit_password_lines:
                    continue

                issues.append({
                    "severity": secret.get("severity", "HIGH"),
                    "confidence": "MEDIUM",
                    "test_id": "SECRET",
                    "title": secret.get(
                        "type",
                        "Potential secret detected"
                    ),
                    "file": relative_path,
                    "line": secret_line,
                    "recommendation": (
                        "Move the secret to an environment variable "
                        "and rotate it if it has been exposed."
                    )
                })

        for issue in issues:
            severity = issue.get("severity", "LOW").upper()

            if severity in severity_counts:
                severity_counts[severity] += 1

            issue.setdefault(
                "recommendation",
                "Review this finding and apply an appropriate security fix."
            )

            issue["fix_suggestion"] = suggest_fix(issue)
            issue["file"] = relative_path

        file_issue_count = len(issues)

        results.append({
            "file": relative_path,
            "total_issues": file_issue_count,
            "issues": issues
        })

        total_issues += file_issue_count

    return {
        "project": project_path.name,
        "total_files": len(python_files),
        "total_issues": total_issues,
        "severity_counts": severity_counts,
        "results": results
    }
