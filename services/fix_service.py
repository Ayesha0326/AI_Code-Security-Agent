
from services.report_service import load_report
from autofix.fix_engine import suggest_fix


def get_fix_suggestion(project_id, file_name, issue_line, test_id):
    """
    Return a fix suggestion for a specific issue in a saved scan report.
    Does not modify the original source file.
    """

    if not all((project_id, file_name, test_id)):
        return {
            "success": False,
            "message": "Project ID, file name, and test ID are required."
        }

    if not isinstance(issue_line, int) or issue_line < 1:
        return {
            "success": False,
            "message": "A valid issue line number is required."
        }

    report = load_report(project_id)

    if not report or "error" in report:
        return {
            "success": False,
            "message": "Scan report not found."
        }

    for result in report.get("results", []):
        if result.get("file") != file_name:
            continue

        for issue in result.get("issues", []):
            if (
                issue.get("line") == issue_line
                and issue.get("test_id") == test_id
            ):
                return {
                    "success": True,
                    "file": file_name,
                    "line": issue_line,
                    "test_id": test_id,
                    "title": issue.get("title"),
                    "severity": issue.get("severity"),
                    "fix_suggestion": issue.get("fix_suggestion")
                    or suggest_fix(issue),
                    "requires_review": True,
                    "message": (
                        "Suggestion retrieved. Review it before "
                        "making any code changes."
                    )
                }

    return {
        "success": False,
        "message": "The requested issue was not found in the scan report."
    }
