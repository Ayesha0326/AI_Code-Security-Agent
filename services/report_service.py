
import json
import re

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_FOLDER = BASE_DIR / "reports"

REPORT_FOLDER.mkdir(parents=True, exist_ok=True)


def save_report(project_id, report_data):
    """Save a scan report as a JSON file."""

    if not isinstance(project_id, str) or not re.fullmatch(
        r"[a-f0-9]{32}", project_id
    ):
        return {
            "success": False,
            "message": "Invalid project ID."
        }

    report_path = REPORT_FOLDER / f"{project_id}.json"

    try:
        report_path.write_text(
            json.dumps(report_data, indent=2),
            encoding="utf-8"
        )

        return {
            "success": True,
            "message": "Report saved successfully.",
            "project_id": project_id
        }

    except (OSError, TypeError, ValueError):
        return {
            "success": False,
            "message": "Could not save the scan report."
        }


def load_report(project_id):
    """Load a previously saved scan report."""

    if not isinstance(project_id, str) or not re.fullmatch(
        r"[a-f0-9]{32}", project_id
    ):
        return {
            "error": "Invalid project ID."
        }

    report_path = REPORT_FOLDER / f"{project_id}.json"

    if not report_path.is_file():
        return {
            "error": "Scan report not found."
        }

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))

        if not isinstance(report, dict):
            return {
                "error": "Invalid scan report format."
            }

        return report

    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "error": "Could not read the scan report."
        }
