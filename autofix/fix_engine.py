
import ast
import os
import shutil
import tempfile
from pathlib import Path

from autofix.patch_validator import validate_patch


def suggest_fix(issue):
    test_id = issue.get("test_id", "")
    title = issue.get("title", "").lower()

    if test_id == "B602" or "shell=true" in title:
        return {
            "fix_available": True,
            "fix_type": "manual_review",
            "description": (
                "Avoid shell=True. Pass the executable and arguments "
                "as a list, after checking how the command is constructed."
            ),
            "example": (
                'subprocess.run(["command", "argument"], check=True)'
            ),
            "risk": "medium",
            "requires_review": True
        }

    if test_id in ("B105", "SECRET") or "hardcoded password" in title:
        return {
            "fix_available": True,
            "fix_type": "environment_variable",
            "description": (
                "Move the password into an environment variable. "
                "Rotate it if it was a real exposed credential."
            ),
            "example": (
                'import os\n'
                'password = os.getenv("APP_PASSWORD")'
            ),
            "risk": "low",
            "requires_review": True
        }

    return {
        "fix_available": False,
        "fix_type": "manual_review",
        "description": "No supported fix is available for this issue yet.",
        "example": None,
        "risk": "unknown",
        "requires_review": True
    }


def create_patch(original_code, fixed_code):
    if not isinstance(original_code, str) or not isinstance(fixed_code, str):
        return {
            "valid": False,
            "message": "Both code versions must be text."
        }

    if not original_code.strip() or not fixed_code.strip():
        return {
            "valid": False,
            "message": "Original and fixed code cannot be empty."
        }

    try:
        ast.parse(fixed_code)
    except SyntaxError as error:
        return {
            "valid": False,
            "message": "Proposed fix has invalid Python syntax.",
            "line": error.lineno
        }

    if original_code == fixed_code:
        return {
            "valid": False,
            "message": "No changes were made."
        }

    return {
        "valid": True,
        "message": "Patch created. Review before applying.",
        "original_code": original_code,
        "fixed_code": fixed_code,
        "requires_review": True
    }


def apply_patch(file_path, fixed_code):
    target = Path(file_path).resolve()
    temporary_path = None

    if not target.is_file() or target.suffix.lower() != ".py":
        return {
            "success": False,
            "message": "A valid existing Python file is required."
        }

    try:
        original_code = target.read_text(encoding="utf-8")

        validation = validate_patch(original_code, fixed_code)

        if not isinstance(validation, dict) or not validation.get("valid"):
            return {
                "success": False,
                "message": (
                    validation.get("message", "Patch validation failed.")
                    if isinstance(validation, dict)
                    else "Patch validation failed."
                )
            }

        # Check syntax again before preparing any file changes.
        try:
            ast.parse(fixed_code)
        except SyntaxError as error:
            return {
                "success": False,
                "message": "Proposed fix has invalid Python syntax.",
                "line": error.lineno
            }

        backup_path = target.with_suffix(target.suffix + ".bak")

        if backup_path.exists():
            return {
                "success": False,
                "message": (
                    "Backup already exists. Review or safely preserve "
                    "the existing backup before retrying."
                )
            }

        # Prepare the replacement in the same directory.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(fixed_code)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        # Preserve the original file before replacing it.
        shutil.copy2(target, backup_path)

        # Replace the file only after validation and backup succeed.
        os.replace(temporary_path, target)
        temporary_path = None

        return {
            "success": True,
            "message": "Patch applied. Backup created.",
            "backup_path": str(backup_path),
            "requires_review": True,
            "requires_rescan": True
        }

    except (OSError, UnicodeError) as error:
        return {
            "success": False,
            "message": "Could not safely apply the patch.",
            "details": str(error)
        }

    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
