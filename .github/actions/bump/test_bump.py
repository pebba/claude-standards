"""Runnable check for bump.py: python .github/actions/bump/test_bump.py"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bump  # noqa: E402

assert bump.next_version("1.2.3", "fix: crash on empty csv (#4)") == "1.2.4"
assert bump.next_version("1.2.3", "feat(ui): dark mode") == "1.3.0"
assert bump.next_version("1.2.3", "feat!: drop android 7") == "2.0.0"
assert bump.next_version("1.2.3", "refactor: x", "BREAKING CHANGE: db schema") == "2.0.0"
assert bump.next_version("1.2.3", "Update readme") == "1.2.4"
assert bump.next_version("0.0.0", "feat: initial standards") == "0.1.0"

s = bump.changelog_section("1.3.0", "feat(ui): dark mode (#12)", "", "pebba/x", "2026-10-18")
assert s == "## [1.3.0] - 2026-10-18\n\n### Added\n\n- dark mode ([#12](https://github.com/pebba/x/pull/12))\n", s
assert "### Fixed" in bump.changelog_section("1.2.4", "fix: y", "", "", "d")
assert "**Breaking:**" in bump.changelog_section("2.0.0", "feat!: z", "", "", "d")

with tempfile.TemporaryDirectory() as d:
    os.chdir(d)
    Path("pubspec.yaml").write_text("name: app\nversion: 1.2.3+7\n\nenvironment:\n", encoding="utf-8")
    Path("pyproject.toml").write_text('[project]\nname = "app"\nversion = "1.2.3"\n\n[tool.x]\nversion = "keep"\n', encoding="utf-8")
    Path(".claude-plugin").mkdir()
    Path(".claude-plugin/plugin.json").write_text('{"name": "std", "version": "1.2.3"}', encoding="utf-8")
    assert bump.file_version() == "1.2.3"
    bump.write_version("1.3.0")
    assert "version: 1.3.0+8\n\nenvironment:" in Path("pubspec.yaml").read_text(encoding="utf-8")
    py = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.3.0"' in py and 'version = "keep"' in py
    assert json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"] == "1.3.0"

    for f in ("pubspec.yaml", "pyproject.toml", ".claude-plugin/plugin.json"):
        Path(f).unlink()
    Path("package.json").write_bytes(b'{\r\n  "name": "web",\r\n  "version": "0.4.2",\r\n  "deps": {"x": {"version": "9.9.9"}}\r\n}\r\n')
    Path("build.gradle.kts").write_text('plugins { java }\ngroup = "a"\nversion = "0.4.2"\n', encoding="utf-8")
    assert bump.file_version() == "0.4.2"
    bump.write_version("0.5.0")
    pkg = Path("package.json").read_bytes()
    assert b'"version": "0.5.0",\r\n' in pkg and b'"version": "9.9.9"' in pkg, pkg
    assert 'version = "0.5.0"' in Path("build.gradle.kts").read_text(encoding="utf-8")

    bump.write_changelog("## [1.0.0] - d\n\n- a\n")
    bump.write_changelog("## [1.1.0] - d\n\n- b\n")
    log = Path("CHANGELOG.md").read_text(encoding="utf-8")
    assert log.startswith("# Changelog\n") and log.index("[1.1.0]") < log.index("[1.0.0]"), log
    os.chdir(Path(__file__).parent)

print("bump: all checks passed")
