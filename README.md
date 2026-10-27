# SecureCode AI — AI Code Security Agent

SecureCode AI is a Python-based web application designed to help identify potential security issues in source code and support automated fixes for selected vulnerabilities.

## Features

- Upload source code for security scanning.
- Identify potential vulnerabilities using security scanning tools.
- Generate automated fixes for supported vulnerability types.
- Validate supported fixes through rescanning.
- Web-based interface for interacting with the scanner.

## Tech Stack

- Python
- Flask
- Bandit
- HTML
- CSS
- JavaScript

## Project Structure

- `app.py` — Flask application and API routes
- `scanner/` — Security scanning functionality
- `autofix/` — Automated fix functionality
- `services/` — Supporting application services
- `frontend/` — Web interface
- `tests` — Test scripts

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI-Code-Security-Agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On Windows Git Bash:

```bash
source venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open the local address displayed by Flask in your terminal.

## Testing

Run the available tests with:

```bash
python -m pytest -v
```

## Project Status

This is a practical software security project under development. Scanning and automated-fix capabilities depend on the supported vulnerability types and the current implementation.

## Disclaimer

This tool is intended for educational and defensive software security purposes. Review all suggested fixes and test them before applying them to production systems.

## Author

Ayesha Yaseen

GitHub: https://github.com/Ayesha0326

Portfolio: https://ayesha-yaseen-portfolio.vercel.app/
