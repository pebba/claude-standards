# Monthly drift check (runs unattended in CI)

This repo is pebba/claude-standards: a Claude Code plugin marketplace (`pebba`, `.claude-plugin/marketplace.json`) whose single plugin `std` sits at the repo root (`.claude-plugin/plugin.json`, `rules.md`, `hooks/`, `skills/`, `external/`, `templates/`). Your job: keep it aligned with current Claude Code and pull in upstream updates of copied external skills.

Hard rules:
- Edit files in the working tree only. Never commit, push, create branches or open PRs; a later workflow step does that.
- Do not bump versions or edit CHANGELOG.md; the release automation does that.
- No Claude attribution anywhere (no Co-Authored-By, no "Generated with Claude Code", no session links), including in the report.
- Only change something when a source you fetched clearly requires it. If you're unsure, change nothing and list it under "Open questions".

## 1. Claude Code drift

1. Read `.github/drift-state.json` for the Claude Code version the repo was last checked against.
2. Fetch the changelog `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`. Collect every entry newer than that version that touches any of these: plugins, `plugin.json`/`marketplace.json` schema, marketplace sources or auto-update, `claude plugin validate`, skills (SKILL.md frontmatter, invocation, namespacing), hooks (events, `hooks.json` format, input/output fields, Windows shell behaviour), settings keys used here (`extraKnownMarketplaces`, `enabledPlugins`, `attribution`), cloud sessions and plugin sync.
3. Fetch `https://code.claude.com/docs/llms.txt` and from it the current pages on plugins (manifest and marketplace reference, loading/updates), skills, hooks and settings. Check that every key, field, path and behaviour this repo relies on is still documented and not deprecated:
   - `.claude-plugin/*.json`
   - `hooks/hooks.json` and `hooks/guard.sh`, which read `tool_input.command` and `cwd` and deny with exit 2
   - skill frontmatter
   - `templates/settings.json`
   - the update and cloud-session notes in README.md
4. Also check the pinned major versions of the GitHub Actions in `.github/workflows/` and `.github/actions/`. Use `gh api repos/<owner>/<repo>/releases/latest`. Only raise a pin when a new major version exists.
5. Apply minimal fixes. If anything changed in this section, update `.github/drift-state.json` to the newest changelog version you reviewed and today's date.

## 2. External skills

For each row in `external/SOURCES.md`:

1. Run `git ls-remote <repo-url> <ref>` and compare the result with the recorded commit.
2. If upstream moved on:
   - Clone it with `git clone --filter=blob:none <url> /tmp/upstream-<skill>`.
   - Diff the recorded upstream path between the old and the new commit.
   - Apply those upstream changes to `external/<skill>/` while keeping every adaptation listed in the row.
   - Update the row's commit and date.
3. If the upstream LICENSE changed, copy the new one. Flag a license change prominently in the report, and do not apply the update if the license is no longer permissive.

## 3. Report

Write `drift-report.md` at the repo root. It is not committed; it becomes the PR body. Sections:
- **Summary**: one or two lines.
- **Claude Code**: the version range you reviewed; each change you made with the reason and the doc or changelog link.
- **External skills**: per updated skill, the upstream compare link (`https://github.com/<o>/<r>/compare/<old>...<new>`) and what was merged or kept.
- **Open questions**: anything you noticed but deliberately did not change.

If there is nothing to do, write "No drift found." plus the versions and skills you checked, and leave every other file untouched.
