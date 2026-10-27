
import shutil
import uuid
import zipfile

from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS 
from werkzeug.utils import secure_filename
from services.report_service import save_report, load_report
from services.scan_service import scan_project_code
from services.report_service import save_report
from services.fix_service import get_fix_suggestion
from autofix.fix_engine import apply_patch

app = Flask(__name__)
CORS(app)   
BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
REPORT_FOLDER = BASE_DIR / "reports"
EXTRACT_FOLDER = UPLOAD_FOLDER / "extracted"

for folder in (UPLOAD_FOLDER, REPORT_FOLDER, EXTRACT_FOLDER):
    folder.mkdir(parents=True, exist_ok=True)


app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

MAX_EXTRACTED_FILES = 500
MAX_EXTRACTED_SIZE = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 1000


@app.route("/")
def home():
    return jsonify({
        "message": "SecureCode AI Backend is running!",
        "status": "success"
    })


@app.route("/api/upload", methods=["POST"])
def upload_project():
    if "file" not in request.files:
        return jsonify({
            "error": "Please select a ZIP file"
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "error": "No file selected"
        }), 400

    if Path(file.filename).suffix.lower() != ".zip":
        return jsonify({
            "error": "Only ZIP files are allowed"
        }), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({
            "error": "Invalid filename"
        }), 400

    project_id = uuid.uuid4().hex

    save_path = UPLOAD_FOLDER / f"{project_id}_{filename}"
    project_folder = EXTRACT_FOLDER / project_id

    try:
        file.save(save_path)

        with zipfile.ZipFile(save_path, "r") as archive:
            members = archive.infolist()

            if len(members) > MAX_EXTRACTED_FILES:
                return jsonify({
                    "error": "ZIP contains too many files"
                }), 400

            total_size = sum(member.file_size for member in members)

            if total_size > MAX_EXTRACTED_SIZE:
                return jsonify({
                    "error": "Extracted project exceeds 100 MB"
                }), 400

            for member in members:
                if member.flag_bits & 0x1:
                    return jsonify({
                        "error": "Encrypted ZIP files are not supported"
                    }), 400

                member_path = Path(member.filename)

                if (
                    member_path.is_absolute()
                    or ".." in member_path.parts
                    or member_path.drive
                    or member.filename.startswith(("/", "\\"))
                ):
                    return jsonify({
                        "error": "Unsafe path detected in ZIP"
                    }), 400

                if member.is_dir():
                    continue

                if (
                    member.file_size > 0
                    and member.compress_size == 0
                ):
                    return jsonify({
                        "error": "Invalid ZIP entry"
                    }), 400

                if (
                    member.compress_size > 0
                    and member.file_size / member.compress_size
                    > MAX_COMPRESSION_RATIO
                ):
                    return jsonify({
                        "error": "ZIP compression ratio is too high"
                    }), 400

            project_folder.mkdir(parents=True, exist_ok=False)
            resolved_project = project_folder.resolve()

            for member in members:
                target = (
                    project_folder / member.filename
                ).resolve()

                if not target.is_relative_to(resolved_project):
                    return jsonify({
                        "error": "Unsafe ZIP path detected"
                    }), 400

            archive.extractall(project_folder)

        result = scan_project_code(project_folder)

        report_status = save_report(project_id, result)

        if not report_status["success"]:
            return jsonify({
                "error": "Could not save the scan report."
            }), 500

        return jsonify({
            "message": "Project uploaded and scanned successfully",
            "project_id": project_id,
            "filename": filename,
            "scan_result": result
        }), 200

    except zipfile.BadZipFile:
        return jsonify({
            "error": "The uploaded ZIP file is invalid or corrupted"
        }), 400

    except Exception:
        app.logger.exception("Project upload or scan failed")

        return jsonify({
            "error": "The project could not be scanned"
        }), 500

    finally:
        save_path.unlink(missing_ok=True)


@app.route("/api/fix-suggestion", methods=["POST"])
def fix_suggestion():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    project_id = data.get("project_id")
    file_name = data.get("file_name")
    issue_line = data.get("issue_line")
    test_id = data.get("test_id")

    if (
        not isinstance(project_id, str)
        or not isinstance(file_name, str)
        or not isinstance(test_id, str)
        or not isinstance(issue_line, int)
        or isinstance(issue_line, bool)
    ):
        return jsonify({
            "success": False,
            "message": (
                "project_id, file_name, test_id, and "
                "a numeric issue_line are required."
            )
        }), 400

    result = get_fix_suggestion(
        project_id=project_id,
        file_name=file_name,
        issue_line=issue_line,
        test_id=test_id
    )

    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@app.route("/api/apply-fix", methods=["POST"])
def apply_fix_route():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON request body is required."
        }), 400

    project_id = data.get("project_id")
    file_name = data.get("file_name")
    fixed_code = data.get("fixed_code")
    confirm_apply = data.get("confirm_apply")

    if (
        not isinstance(project_id, str)
        or len(project_id) != 32
        or any(c not in "0123456789abcdef" for c in project_id)
    ):
        return jsonify({
            "success": False,
            "message": "Invalid project ID."
        }), 400

    if (
        not isinstance(file_name, str)
        or not file_name.strip()
        or not isinstance(fixed_code, str)
        or not fixed_code.strip()
    ):
        return jsonify({
            "success": False,
            "message": "File name and fixed code are required."
        }), 400

    if confirm_apply is not True:
        return jsonify({
            "success": False,
            "message": "Review the code and confirm before applying."
        }), 400

    project_folder = (EXTRACT_FOLDER / project_id).resolve()
    target_path = (project_folder / file_name).resolve()

    if not target_path.is_relative_to(project_folder):
        return jsonify({
            "success": False,
            "message": "Invalid file path."
        }), 400

    if target_path.suffix.lower() != ".py":
        return jsonify({
            "success": False,
            "message": "Only Python files are supported."
        }), 400

    if not target_path.is_file():
        return jsonify({
            "success": False,
            "message": "Project file not found."
        }), 404

    try:
        result = apply_patch(target_path, fixed_code)

        if not isinstance(result, dict):
            return jsonify({
                "success": False,
                "message": "Unexpected response from the fix engine."
            }), 500

        status_code = 200 if result.get("success") else 400
        return jsonify(result), status_code

    except Exception:
        app.logger.exception("Applying reviewed fix failed")
        return jsonify({
            "success": False,
            "message": "Could not apply the fix."
        }), 500

@app.route("/api/report/<project_id>", methods=["GET"])
def get_scan_report(project_id):
    report = load_report(project_id)

    if "error" in report:
        return jsonify({
            "success": False,
            "message": report["error"]
        }), 404

    return jsonify({
        "success": True,
        "report": report
    }), 200


@app.route("/api/history", methods=["GET"])
def scan_history():
    history = []

    for report_file in REPORT_FOLDER.glob("*.json"):
        project_id = report_file.stem

        report = load_report(project_id)

        if "error" in report:
            continue

        history.append({
            "project_id": project_id,
            "total_files": report.get("total_files", 0),
            "total_issues": report.get("total_issues", 0),
            "severity_counts": report.get("severity_counts", {}),
            "created_at": report_file.stat().st_mtime
        })

    history.sort(
        key=lambda item: item["created_at"],
        reverse=True
    )

    return jsonify({
        "success": True,
        "total_scans": len(history),
        "history": history
    }), 200

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "File is too large. Maximum size is 20 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
