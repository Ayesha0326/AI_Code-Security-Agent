
import tempfile
from pathlib import Path

from autofix.fix_engine import (
    suggest_fix,
    create_patch,
    apply_patch
)
from autofix.patch_validator import validate_python_code


# 1. Test fix suggestion
issue = {
    "test_id": "B602",
    "title": "subprocess call with shell=True identified"
}

suggestion = suggest_fix(issue)

print("1. Fix suggestion:", suggestion["fix_available"])
print("Description:", suggestion["description"])


# 2. Test syntax validation
valid_result = validate_python_code('print("Hello")')
invalid_result = validate_python_code('if True print("Hello")')

print("\n2. Valid syntax:", valid_result["valid"])
print("Invalid syntax rejected:", not invalid_result["valid"])


# 3. Test patch creation
original_code = 'message = "old"\n'
fixed_code = 'message = "updated"\n'

patch = create_patch(original_code, fixed_code)

print("\n3. Patch created:", patch["valid"])


# 4. Test patch application using a temporary file
with tempfile.TemporaryDirectory() as temp_dir:
    test_file = Path(temp_dir) / "sample.py"
    test_file.write_text(original_code, encoding="utf-8")

    result = apply_patch(test_file, fixed_code)

    print("\n4. Patch applied:", result["success"])
    print("Backup created:", Path(str(test_file) + ".bak").is_file())
    print("Updated content:", test_file.read_text(encoding="utf-8").strip())
