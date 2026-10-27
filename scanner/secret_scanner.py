
import re
from pathlib import Path


SECRET_PATTERNS = {
    "Possible hardcoded password": re.compile(
        r"""(?i)\b(password|passwd|pwd)\s*[:=]\s*["'][^"']{4,}["']"""
    ),
    "Possible API key or secret": re.compile(
        r"""(?i)\b(api_key|apikey|secret_key|access_token|auth_token)\s*[:=]\s*["'][^"']{8,}["']"""
    ),
    "Possible private key": re.compile(
        r"""-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"""
    ),
}


def scan_secrets(file_path):
    file_path = Path(file_path)

    if not file_path.is_file() or file_path.suffix != ".py":
        return {
            "error": "A valid Python file is required."
        }

    findings = []

    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as file:
            for line_number, line in enumerate(file, start=1):
                for secret_type, pattern in SECRET_PATTERNS.items():
                    if pattern.search(line):
                        findings.append({
                            "type": secret_type,
                            "severity": "HIGH",
                            "file": str(file_path),
                            "line": line_number,
                            "message": (
                                "Potential hardcoded secret detected. "
                                "Review this line and move secrets to "
                                "environment variables."
                            )
                        })
                        break

        return {
            "file": str(file_path),
            "total_secrets": len(findings),
            "secrets": findings
        }

    except OSError:
        return {
            "error": "Could not read the file."
        }
