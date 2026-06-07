"""Deploy git-tracked project files to PythonAnywhere via their API."""

import subprocess
import sys
from pathlib import Path

import requests

PA_USER = "toonarmycaptain"
PA_HOST = "www.pythonanywhere.com"
API_BASE = f"https://{PA_HOST}/api/v0/user/{PA_USER}"
WEBAPP_DOMAIN = f"{PA_USER}.pythonanywhere.com"

PROJECT_DIR = Path(__file__).parent
REMOTE_DIR = f"/home/{PA_USER}/toonarmycaptain_website"

SECRETS_FILE = PROJECT_DIR / ".secrets"

SKIP_PREFIXES = (
    ".appveyor.yml",
    ".coveragerc",
    ".dcignore",
    ".github/",
    ".pyup.yml",
    ".whitesource",
    "mypy.ini",
    "requirements_dev.txt",
    "tests/",
    "README.md",
    "deploy.py",
)


def _get_git_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        f
        for f in result.stdout.splitlines()
        if f and not f.startswith(SKIP_PREFIXES)
    ]


def _load_token() -> str:
    if SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.startswith("PA_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    return ""


def upload_file(
    session: requests.Session, local_path: Path, remote_path: str
) -> bool:
    url = f"{API_BASE}/files/path{remote_path}"
    with open(local_path, "rb") as f:
        resp = session.post(url, files={"content": f})
    if resp.status_code in (200, 201):
        print(f"  OK: {remote_path}")
        return True
    print(f"  FAIL ({resp.status_code}): {remote_path} — {resp.text}")
    return False


def main() -> None:
    token = _load_token()
    if not token:
        token = input("PythonAnywhere API token: ").strip()
    if not token:
        print("No token provided. Set PA_API_TOKEN= in .secrets or enter it when prompted.")
        sys.exit(1)

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    files = _get_git_files()
    if not files:
        print("No files to upload.")
        sys.exit(1)

    print(f"\nUploading {len(files)} file(s) to {PA_HOST} as {PA_USER}...")
    failures = 0
    for rel_path in files:
        local = PROJECT_DIR / rel_path
        if not local.exists():
            print(f"  SKIP (not found): {rel_path}")
            continue
        remote = f"{REMOTE_DIR}/{rel_path}"
        if not upload_file(session, local, remote):
            failures += 1

    if failures:
        print(f"\n{failures} file(s) failed to upload.")
        sys.exit(1)

    print("\nAll files uploaded.")

    print("\nReloading web app...")
    resp = session.post(f"{API_BASE}/webapps/{WEBAPP_DOMAIN}/reload/")
    if resp.status_code == 200:
        print("  Web app reloaded.")
    else:
        print(f"  Reload failed ({resp.status_code}): {resp.text}")


if __name__ == "__main__":
    main()
