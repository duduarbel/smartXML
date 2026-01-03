#!/usr/bin/env python3
"""
Deploy a Python package to PyPI.

Steps:
1) Get version number as a parameter.
2) Verify version matches pyproject.toml.
3) Verify CHANGELOG.md contains an entry for that version.
4) python -m build
5) python -m twine upload dist/* (using key from ~/pypi.txt)
"""

from __future__ import annotations

import argparse
import glob
import re
import shutil
import subprocess
import sys
import os
from pathlib import Path


class DeployError(RuntimeError):
    pass


def run_command(command: list[str], env: dict[str, str] = None) -> None:
    print(f"+ {' '.join(command)}")
    completed = subprocess.run(command, text=True, env=env)
    if completed.returncode != 0:
        raise DeployError(f"Command failed with exit code {completed.returncode}: {' '.join(command)}")


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DeployError(f"Missing required file: {path}") from exc


def verify_version_in_pyproject(pyproject_path: Path, expected_version: str) -> None:
    """
        Verify pyproject.toml contains: version = "<expected_version>"

    This is a pragmatic check without requiring a TOML parser.
    If you have a more complex layout (dynamic versioning, tool-specific version fields),
    you should adapt this accordingly.
    """
    contents = read_text_file(pyproject_path)

    # Match a PEP 621-style version key:
    # version = "1.2.3"
    version_pattern = re.compile(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$')
    match = version_pattern.search(contents)
    if not match:
        raise DeployError(
            f'Could not find a PEP 621 version line in {pyproject_path} (expected: version = "{expected_version}").'
        )

    found_version = match.group(1).strip()
    if found_version != expected_version:
        raise DeployError(
            f"Version mismatch:\n" f"  expected: {expected_version}\n" f"  found in {pyproject_path}: {found_version}"
        )

    print(f"OK: {pyproject_path} version matches {expected_version}")


def verify_changelog_entry(changelog_path: Path, expected_version: str) -> None:
    """
        Verify CHANGELOG.md contains an entry for the version.

    This supports common patterns like:
    - '## 1.2.3'
    - '## [1.2.3] - 2025-01-01'
    - '# 1.2.3' (less common)
    """
    contents = read_text_file(changelog_path)

    escaped = re.escape(expected_version)
    entry_patterns = [
        re.compile(rf"(?m)^\s*##\s*\[?{escaped}\]?\b"),
        re.compile(rf"(?m)^\s*#\s*\[?{escaped}\]?\b"),
        re.compile(rf"(?m)^\s*##\s*Version\s*{escaped}\b"),
    ]

    if not any(pattern.search(contents) for pattern in entry_patterns):
        raise DeployError(
            f"Did not find a changelog entry for version {expected_version} in {changelog_path}.\n"
            f"Expected a heading like '## {expected_version}' or '## [{expected_version}] - YYYY-MM-DD'."
        )

    print(f"OK: {changelog_path} contains an entry for {expected_version}")


def ensure_tools_available() -> None:
    """
    Check that build and twine are available in the current interpreter env.
    """
    for module_name in ["build", "twine"]:
        print(f"Checking module availability: {module_name}")
        result = subprocess.run([sys.executable, "-c", f"import {module_name}"], text=True)
        if result.returncode != 0:
            raise DeployError(
                f"Required module '{module_name}' is not available in this environment.\n"
                f"Install it with: {sys.executable} -m pip install {module_name}"
            )


def clean_dist(dist_dir: Path) -> None:
    if dist_dir.exists():
        print(f"Removing existing {dist_dir}/")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy the package to PyPI.")
    parser.add_argument(
        "version",
        help="Version to deploy (must match pyproject.toml and be present in CHANGELOG.md).",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Do not remove the dist/ directory before building.",
    )
    args = parser.parse_args()

    version = args.version.strip()
    pyproject_path = Path("pyproject.toml")
    changelog_path = Path("changelog.md")

    ensure_tools_available()
    verify_version_in_pyproject(pyproject_path, version)
    verify_changelog_entry(changelog_path, version)

    dist_dir = Path("dist")
    if not args.skip_clean:
        clean_dist(dist_dir)

    # add git tag
    run_command(["git", "tag", args.version.strip()])
    run_command(["git", "push", "origin", args.version.strip()])

    # Build
    run_command([sys.executable, "-m", "build"])

    # # Verify artifacts exist
    artifacts = sorted(glob.glob("dist/*"))
    if not artifacts:
        raise DeployError("Build produced no artifacts in dist/. Aborting upload.")

    pypi_file = Path(f"{Path.home()}/ex/pypi.txt")
    if not pypi_file.expanduser().is_file():
        raise DeployError(f"Missing PyPI API key file: {pypi_file.expanduser()}")

    key = pypi_file.read_text()
    env = os.environ.copy()
    env["TWINE_USERNAME"] = "__token__"
    env["TWINE_PASSWORD"] = key
    twine_command = [sys.executable, "-m", "twine", "upload", "dist/*"]
    run_command(twine_command, env=env)

    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeployError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
