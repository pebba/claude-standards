---
name: python-exe-build
description: Build a Python app into a single Windows .exe with PyInstaller (via uv), locally or in CI. Covers the entry point, bundling data files, embedding the version, GUI vs console apps, and fixing missing-module or antivirus problems.
when_to_use: Use when the user wants a Windows executable from Python, mentions "exe bauen", "PyInstaller", "pyinstaller", "standalone", "onefile", "ausführbare Datei", or a frozen exe that crashes, misses modules or data files, or is flagged by antivirus.
---

# Python .exe build (PyInstaller)

CI builds and publishes the exe automatically (`release-python.yml` on `windows-latest`). This skill covers local builds and the settings CI needs. PyInstaller can't cross-compile, so the exe must be built on Windows.

## Local build

```bash
uv sync
uv run pytest
uv run --with pyinstaller pyinstaller --onefile --name <app> src/<app>/__main__.py
# -> dist/<app>.exe
```

- The asset name stays `<app>.exe` (no version in the file name), so `releases/latest/download/<app>.exe` always works.
- For GUI apps (Tk, Qt, …), add `--noconsole` so no console window appears.
- Put extra flags in the release workflow's `pyinstaller-args` input so CI and local builds match.

## Version inside the exe

`pyproject.toml` `version` is owned by the release workflow; don't edit it by hand. Read it at runtime:

```python
from importlib.metadata import version
__version__ = version("<dist-name>")
```

Add `--copy-metadata <dist-name>` to the PyInstaller flags; without it the frozen app raises `PackageNotFoundError`.

## Data files and hidden imports

- **Data files:** `--add-data "src/<app>/assets;<app>/assets"`. Use `;` on Windows, `:` elsewhere. At runtime, resolve paths from the bundle root: `Path(getattr(sys, "_MEIPASS", Path(__file__).parent))`.
- **Missing module at runtime:** add `--hidden-import <module>`, or `--collect-all <package>` for plugin-heavy packages.
- **Debugging:** build once without `--onefile` and with `--console`, then run `dist/<app>/<app>.exe` from a terminal to see the traceback.

## Troubleshooting

- **Antivirus or SmartScreen flags the exe:** this is common for unsigned onefile builds. Mitigations:
  - Build with an up-to-date PyInstaller (bootloaders are rebuilt each release).
  - Avoid UPX (`--noupx`).
  - Code-sign the exe if it gets distributed beyond personal use.
- **Slow startup:** onefile unpacks to a temp dir on every start. A `--onedir` build zipped as an artifact starts faster, but changes the asset name, so discuss it with the user first.
- **Tests run on Linux in CI** (`ci-python.yml`). For Windows-only code, set the CI input `os: windows-latest`.
