# CLAUDE.md: claude-standards

This repo is pebba's Claude Code plugin marketplace (`pebba`) with one plugin, `std`, at the repo root. It is the single source for conventions that apply to all of pebba's repos. The plugin's rules (`rules.md`) apply here too.

Never add Claude attribution (Co-Authored-By, "Generated with Claude Code", session links) to commits, PRs, tags, release notes or CHANGELOG.

## Commands

- Validate manifests, skills and hooks: `claude plugin validate . --strict`
- Guard hook check: `bash hooks/guard.test.sh` (Git Bash on Windows, any bash on Linux)
- Bump logic check: `python .github/actions/bump/test_bump.py`
- Try the plugin from the working tree without installing it: `claude --plugin-dir .`

## Layout

- `.claude-plugin/`: `marketplace.json` (catalog, plugin `std` with source `./`) and `plugin.json`. Its `version` is written only by the release workflow.
- `rules.md`: standing rules, injected by the SessionStart hook. Keep it well under 10,000 characters, the hook output cap.
- `hooks/`: `hooks.json`, `guard.sh` (blocks pushes to main and attribution) and its test.
- `skills/<name>/SKILL.md`: own skills, invoked as `/std:<name>`. `external/`: copied third-party skills plus `SOURCES.md`.
- `templates/`: files `/std:new-repo` copies into other repos.
- `.github/actions/`: `bump` (version + CHANGELOG) and `publish` (commit, tag, release), shared by every repo's release.
- `.github/workflows/`: this repo's `validate`, `release` and `drift-check`, plus the reusable `conventions`, `ci-*` and `release-*` workflows other repos call `@main`.

## Rules for this repo

- Other repos call the reusable workflows and actions at `@main`. Any change to their inputs or behaviour must stay backwards compatible, or every caller has to be updated in the same rollout.
- New skills need a `description` that leads with the use case and a `when_to_use` with the phrases the user actually says (German and English).
- Shell in hooks must run in Git Bash on Windows and in bash on Linux: no jq, no GNU-only flags beyond what Git Bash ships.
- Don't add a top-level `bin/` directory, because claude.ai plugin sync rejects plugins that have one.
