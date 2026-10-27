
import ast


def validate_python_code(code):
    if not isinstance(code, str) or not code.strip():
        return {
            "valid": False,
            "message": "No Python code provided."
        }

    try:
        ast.parse(code)
        return {
            "valid": True,
            "message": "Python syntax validation passed."
        }

    except SyntaxError as error:
        return {
            "valid": False,
            "message": "Python syntax validation failed.",
            "line": error.lineno,
            "details": error.msg
        }


def validate_patch(original_code, fixed_code):
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

    if original_code == fixed_code:
        return {
            "valid": False,
            "message": "No changes detected."
        }

    syntax_result = validate_python_code(fixed_code)

    if not syntax_result["valid"]:
        return syntax_result

    return {
        "valid": True,
        "message": "Patch passed syntax checks. Review before applying.",
        "requires_review": True
    }
