---
name: new-repo
description: Set up a new or existing GitHub repo with pebba's standards. Covers squash-only merge settings, the protected main ruleset, a release deploy key, Claude settings with attribution off, CLAUDE.md, CHANGELOG.md, a README with a latest-release link, and CI/release workflows for Flutter (APK+AAB) or Python (.exe).
when_to_use: Use when the user wants to create a new repo or project, bootstrap or onboard an existing repo onto the standards, "neues Repo anlegen", "Repo aufsetzen", "Standards einrichten", or add CI/release automation to a Flutter or Python project.
argument-hint: "<repo-name> <flutter|python|generic> [public|private]"
---

# New repo

Templates live in `${CLAUDE_PLUGIN_ROOT}/templates`. Work through the steps in order and report what was done. If repo name, stack (`flutter` | `python` | `generic` for web apps, bots and anything without an APK/EXE artifact), visibility or app name (the asset base name, e.g. `3coq`) are missing from `$ARGUMENTS`, ask for them once, together.

## 1. Repo

- **New:** `gh repo create pebba/<name> --<public|private> --clone`, then `cd` into it.
- **Existing:** work in its clone. Check `git status` is clean and stay on `main` for the initial setup.

## 2. Project skeleton (only if empty)

- **Flutter:** `flutter create --org <reverse-domain> --project-name <dart_name> .`. Set `version: 0.0.0+0` in `pubspec.yaml`.
- **Python:**
  1. Run `uv init --package --name <name> .` and set `version = "0.0.0"` in `pyproject.toml`.
  2. Run `uv add --dev ruff pytest`.
  3. Add one smoke test in `tests/`, because pytest exits non-zero when it collects no tests.
  4. The entry point is `src/<name>/__main__.py`.

## 3. Standard files

1. Copy `templates/settings.json` to `.claude/settings.json`. It turns on the marketplace and plugin and switches attribution off; it's also the only attribution setting cloud sessions read.
2. Copy `templates/CLAUDE.md` to `CLAUDE.md`. Fill in what you know (commands for the stack, layout) and delete sections that stay empty.
3. Copy `templates/CHANGELOG.md` to `CHANGELOG.md`.
4. Copy `templates/workflows/<stack>/release.yml` and `ci.yml` (flutter/python) or `pr.yml` (generic: only the PR-title/attribution check, the repo keeps its own CI) to `.github/workflows/`. Replace `APP_NAME`, and for Python the `entry` path.
5. Make sure `.gitignore` contains these lines (append the missing ones):
   - `.claude/settings.local.json`
   - `.env` and `!.env.example`
   - Flutter: `android/key.properties`, `*.jks`, `*.keystore`
   - Python: `dist/`, `build/`, `*.spec`
6. `README.md` must contain, near the top:
   ```markdown
   **[⬇ Latest release](https://github.com/pebba/<name>/releases/latest)**: direct download: [<app>.apk](https://github.com/pebba/<name>/releases/latest/download/<app>.apk)
   ```
   Use `<app>.exe` for Python. For Flutter, also link the `.aab`, or say it's for Play Console upload.

## 4. Initial commit and push

1. `git add -A && git commit -m "chore: initial project setup"`. No Claude attribution.
2. `git push -u origin main`. This is the one direct push to `main` the guard allows, because `main` doesn't exist on the remote yet. If the repo already has `main`, put the files on a branch and open a PR instead.

## 5. GitHub settings

Run these with `gh`. Each must succeed; show any error.

1. Merge settings:
   ```bash
   gh api -X PATCH repos/pebba/<name> -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
     -F delete_branch_on_merge=true -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY
   ```
2. Release deploy key: the release workflow pushes the version commit and tag with it. It's the only bypass actor on `main`.
   ```bash
   k="$(mktemp -d)/release"; ssh-keygen -t ed25519 -N "" -C "release@<name>" -f "$k" -q
   gh repo deploy-key add "$k.pub" -R pebba/<name> --allow-write --title release
   gh secret set RELEASE_KEY -R pebba/<name> < "$k"
   rm -f "$k" "$k.pub"
   ```
3. Ruleset:
   ```bash
   gh api -X POST repos/pebba/<name>/rulesets --input "${CLAUDE_PLUGIN_ROOT}/templates/ruleset.json"
   ```
   It requires PRs, squash only, linear history, no force-push or deletion, and the required check `ci / test`. After the first CI run, compare the check name with `gh pr checks` and fix it in the ruleset if it differs. Generic repos: point it at the repo's own PR check, or drop the `required_status_checks` rule if there is none.
4. Flutter only, signing: tell the user to create an upload keystore once and set four secrets. Without them, release APKs are debug-signed and won't install over each other. Never generate or store the keystore password yourself.
   ```bash
   keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
   base64 -w0 upload-keystore.jks | gh secret set ANDROID_KEYSTORE_BASE64 -R pebba/<name>
   gh secret set ANDROID_KEYSTORE_PASSWORD -R pebba/<name>
   gh secret set ANDROID_KEY_ALIAS -R pebba/<name>
   gh secret set ANDROID_KEY_PASSWORD -R pebba/<name>
   ```
   Also show them the `key.properties` block for `android/app/build.gradle.kts` from `/std:flutter-build`.

## 6. Verify

- `gh api repos/pebba/<name> --jq '{squash: .allow_squash_merge, merge: .allow_merge_commit, rebase: .allow_rebase_merge, del: .delete_branch_on_merge}'`
- `gh api repos/pebba/<name>/rulesets --jq '.[].name'` lists `protect-main`.
- `gh secret list -R pebba/<name>` lists `RELEASE_KEY`.
- Report the remaining manual steps (signing secrets, first PR) and suggest a first feature branch to exercise CI and `/std:release`.
