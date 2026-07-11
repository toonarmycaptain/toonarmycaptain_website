"""Deploy git-tracked project files to PythonAnywhere via their API."""

import argparse
import subprocess
import sys
import time
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
    ".github/",
    ".pre-commit-config.yaml",
    "tests/",
    "README.md",
    "deploy.py",
)

# What counts as "code" for the --code flag: Python modules plus anything
# under a templates/ directory. Everything else (images, other static assets)
# is skipped, so a code/template edit doesn't re-upload every PNG.
CODE_SUFFIXES = (".py",)
CODE_DIRS = ("templates",)


def _is_code(rel_path: str) -> bool:
    p = Path(rel_path)
    return p.suffix.lower() in CODE_SUFFIXES or any(d in CODE_DIRS for d in p.parts)


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


def _get_uncommitted_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
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


def _get_files_since(commit: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", commit, "HEAD"],
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


def _get_changes_files() -> list[str]:
    """Tracked files that differ from HEAD (staged or unstaged).

    Includes files you've `git add`-ed but not yet committed, so you can test
    them before committing; untracked files are excluded.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
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
    for attempt in range(5):
        with open(local_path, "rb") as f:
            resp = session.post(url, files={"content": f})
        if resp.status_code in (200, 201):
            print(f"  OK: {remote_path}")
            return True
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"  Throttled, retrying in {wait}s: {remote_path}")
            time.sleep(wait)
            continue
        print(f"  FAIL ({resp.status_code}): {remote_path} — {resp.text}")
        return False
    print(f"  FAIL (throttled after retries): {remote_path}")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy to PythonAnywhere")
    parser.add_argument(
        "--uncommitted-changes",
        action="store_true",
        help="Upload only staged files instead of all git-tracked files",
    )
    parser.add_argument(
        "--since-commit",
        metavar="SHA",
        help="Upload only files changed since the given commit",
    )
    parser.add_argument(
        "--changes",
        action="store_true",
        help="Upload only tracked files changed vs HEAD (staged + unstaged; "
        "git-added new files included, untracked excluded)",
    )
    parser.add_argument(
        "--code",
        action="store_true",
        help="Upload only code — Python modules and templates/ — "
        "skipping images and other static assets",
    )
    args = parser.parse_args()

    token = _load_token()
    if not token:
        token = input("PythonAnywhere API token: ").strip()
    if not token:
        print("No token provided. Set PA_API_TOKEN= in .secrets or enter it when prompted.")
        sys.exit(1)

    session = requests.Session()
    session.headers["Authorization"] = f"Token {token}"

    if args.since_commit:
        files = _get_files_since(args.since_commit)
        label = f"changed since {args.since_commit[:8]}"
    elif args.changes:
        files = _get_changes_files()
        label = "changed vs HEAD"
    elif args.uncommitted_changes:
        files = _get_uncommitted_files()
        label = "staged"
    else:
        files = _get_git_files()
        label = "git-tracked"

    if args.code:
        files = [f for f in files if _is_code(f)]
        label = f"code ({label})"

    if not files:
        print(f"No {label} files to upload.")
        sys.exit(0)

    print(f"\nUploading {len(files)} {label} file(s) to {PA_HOST} as {PA_USER}...")
    failures = 0
    for rel_path in files:
        local = PROJECT_DIR / rel_path
        if not local.exists():
            print(f"  SKIP (not found): {rel_path}")
            continue
        remote = f"{REMOTE_DIR}/{rel_path}"
        if not upload_file(session, local, remote):
            failures += 1
        time.sleep(0.3)

    if failures:
        print(f"\n{failures} file(s) failed to upload.")
        sys.exit(1)

    print("\nAll files uploaded.")

    if any(f in ("pyproject.toml", "uv.lock") for f in files):
        print("\n⚠ pyproject.toml/uv.lock changed — run `uv sync` on the server before reloading.")

    print("\nReloading web app...")
    resp = session.post(f"{API_BASE}/webapps/{WEBAPP_DOMAIN}/reload/")
    if resp.status_code == 200:
        print("  Web app reloaded.")
    else:
        print(f"  Reload failed ({resp.status_code}): {resp.text}")


if __name__ == "__main__":
    main()
