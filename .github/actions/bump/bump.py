"""Compute the next release version from the squash commit on main and write it into the repo.

Base version: the last vX.Y.Z tag, else the version already in the repo's version file, else 0.0.0.
Bump (Conventional Commits subject): "type!:" or "BREAKING CHANGE" in the body -> major, feat -> minor, else patch.
Writes (whichever exist): pubspec.yaml (X.Y.Z+N, N incremented), pyproject.toml, package.json, build.gradle(.kts),
.claude-plugin/plugin.json, and a new CHANGELOG.md section. Prints the version; writes the release notes to argv[1] if given.
"""

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Version files may live in a subdirectory (e.g. a Flutter app in app/); CHANGELOG.md stays at the repo root.
VERSION_DIR = Path(os.environ.get("BUMP_VERSION_DIR") or ".")
PUBSPEC = VERSION_DIR / "pubspec.yaml"
PYPROJECT = VERSION_DIR / "pyproject.toml"
PLUGIN = Path(".claude-plugin/plugin.json")
# One-line versions, edited in place so the rest of the file keeps its formatting. First match per file wins.
LINE_VERSIONS = [
    (PYPROJECT, r'^(version\s*=\s*")(\d+\.\d+\.\d+)(")'),
    (VERSION_DIR / "package.json", r'^(\s*"version"\s*:\s*")(\d+\.\d+\.\d+)(")'),
    (VERSION_DIR / "build.gradle.kts", r'^(version\s*=\s*")(\d+\.\d+\.\d+)(")'),
    (VERSION_DIR / "build.gradle", r"""^(version\s*=?\s*["'])(\d+\.\d+\.\d+)(["'])"""),
]
CHANGELOG = Path("CHANGELOG.md")
HEADER = "# Changelog\n\nAll notable changes to this project are documented here. Versions follow SemVer; entries are generated from squash-merged PR titles.\n"
SECTIONS = {"feat": "Added", "fix": "Fixed"}


def read(path):
    # newline="" keeps CRLF files CRLF when this runs on a Windows runner.
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def next_version(base, subject, body=""):
    major, minor, patch = map(int, base.split("."))
    head = subject.split(":", 1)[0]
    if head.endswith("!") or "BREAKING CHANGE" in body:
        return f"{major + 1}.0.0"
    if re.match(r"feat\b", head):
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def file_version():
    if PUBSPEC.exists():
        m = re.search(r"^version:\s*(\d+\.\d+\.\d+)", read(PUBSPEC), re.M)
        if m:
            return m.group(1)
    for path, pattern in LINE_VERSIONS:
        m = re.search(pattern, read(path), re.M) if path.exists() else None
        if m:
            return m.group(2)
    if PLUGIN.exists():
        return json.loads(PLUGIN.read_text(encoding="utf-8")).get("version", "0.0.0")
    return "0.0.0"


def write_version(version):
    if PUBSPEC.exists():
        text = read(PUBSPEC)
        m = re.search(r"^version:[ \t]*\S+?(?:\+(\d+))?[ \t]*(?=\r?$)", text, re.M)
        build = int(m.group(1) or 0) + 1 if m else 1
        line = f"version: {version}+{build}"
        text = text.replace(m.group(0), line, 1) if m else text.rstrip("\n") + f"\n{line}\n"
        write(PUBSPEC, text)
    for path, pattern in LINE_VERSIONS:
        if path.exists():
            write(path, re.sub(pattern, rf"\g<1>{version}\g<3>", read(path), count=1, flags=re.M))
    if PLUGIN.exists():
        data = json.loads(PLUGIN.read_text(encoding="utf-8"))
        data["version"] = version
        PLUGIN.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def changelog_section(version, subject, body, repo, date):
    m = re.match(r"(\w+)(\([^)]*\))?(!)?:\s*(.+)", subject)
    kind, breaking, text = (m.group(1), m.group(3), m.group(4)) if m else ("", None, subject)
    if repo:
        text = re.sub(r"\(#(\d+)\)", rf"([#\1](https://github.com/{repo}/pull/\1))", text)
    if breaking or "BREAKING CHANGE" in body:
        text = f"**Breaking:** {text}"
    return f"## [{version}] - {date}\n\n### {SECTIONS.get(kind, 'Changed')}\n\n- {text}\n"


def write_changelog(section):
    text = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else HEADER
    i = text.find("\n## [")
    text = text[: i + 1] + section + "\n" + text[i + 1 :] if i >= 0 else text.rstrip("\n") + "\n\n" + section
    CHANGELOG.write_text(text, encoding="utf-8")


def main():
    tag = git("describe", "--tags", "--abbrev=0", "--match", "v[0-9]*.[0-9]*.[0-9]*")
    base = tag[1:] if tag else file_version()
    subject, body = git("log", "-1", "--format=%s"), git("log", "-1", "--format=%b")
    version = next_version(base, subject, body)
    section = changelog_section(version, subject, body, os.environ.get("GITHUB_REPOSITORY", ""), datetime.date.today().isoformat())
    write_version(version)
    write_changelog(section)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(section.split("\n", 2)[2], encoding="utf-8")
    print(version)


if __name__ == "__main__":
    main()
