# claude-standards

**[⬇ Latest release](https://github.com/pebba/claude-standards/releases/latest)** · [CHANGELOG](CHANGELOG.md)

pebba's personal Claude Code plugin marketplace. It ships one plugin, **`std`**, which brings the same dev conventions into every Claude Code session, locally and in the cloud (web and phone). The conventions are maintained here and nowhere else.

## What the plugin does

| Part | What it does |
| --- | --- |
| **Standing rules** (`rules.md`) | A SessionStart hook injects them into every session, including after `/clear` and compaction. They cover: squash-only merges, few branches, Conventional Commits PR titles, automatic releases, CHANGELOG and latest-release link in every repo, Flutter APK+AAB and Python .exe artifacts, and no Claude attribution. |
| **Guard hook** (`hooks/guard.sh`) | Blocks `git push` to `main`/`master` (except a brand-new repo's first push), and blocks commits, tags, PRs and releases that carry Claude attribution. Runs in Git Bash on Windows and bash on Linux. |
| **`/std:release`** | Checks the PR title, waits for checks, squash-merges, and verifies the automatic release (tag, title, assets, CHANGELOG). |
| **`/std:new-repo`** | Sets up a repo: merge settings, protected `main`, release deploy key, `.claude/settings.json`, CLAUDE.md, CHANGELOG, README release link, and CI and release workflows. |
| **`std:flutter-build`**, **`std:python-exe-build`** | Build know-how for APK/AAB (signing, versioning) and PyInstaller .exe files. |
| **Reusable workflows** | `ci-flutter`, `ci-python`, `release-flutter`, `release-python`, `release-generic` (no artifact: web apps, bots) and `conventions`. Other repos call them `@main`, so CI logic is also maintained only here. |

Skills trigger on their own when the request matches, or explicitly as `/std:<name>`. Plugin skills are always namespaced.

## Install

### Everywhere, via claude.ai sync (recommended)

In claude.ai, go to **Customize → Plugins → Add → Add marketplace**, enter `pebba/claude-standards` and turn on **Sync automatically**. The synced plugin (`std@synced`) loads in cloud sessions (claude.ai/code, mobile app) and in the CLI on any machine where you're signed in to claude.ai. Nothing to install locally or per repo.

Don't also install `std@pebba` locally: a local plugin with the same name takes precedence over the synced one.

### Attribution off, per repo

`/std:new-repo` copies [`templates/settings.json`](templates/settings.json) to the repo's `.claude/settings.json`. It only switches attribution off. That committed file is what turns attribution off in the cloud, because cloud sessions only read project settings. Locally, add the same `attribution` block to `~/.claude/settings.json` to cover every repo.

### Locally, without claude.ai

Only for machines that aren't signed in to claude.ai: `claude plugin marketplace add pebba/claude-standards`, then `claude plugin install std@pebba`. Then turn on auto-update under `/plugin` → Marketplaces. Third-party marketplaces don't auto-update by default.

## How updates reach sessions

- Every merge to `main` bumps `version` in `.claude-plugin/plugin.json`. Clients compare that string, so an unchanged version means no update.
- **Synced:** every cloud session starts on a fresh VM with the plugin version currently synced to your claude.ai account. The CLI picks up the synced version too.
- **Local install:** with `autoUpdate: true`, Claude Code refreshes the marketplace in the background, shortly after the first message of a session. New versions load in the next session, or right away with `/reload-plugins`. Force a refresh with `claude plugin marketplace update pebba`.

## Versioning and releases (same rules as every repo)

1. The PR title is a Conventional Commit (`feat: …`, `fix: …`, `feat!: …`). The squash merge makes it the commit subject on `main`.
2. `release.yml` runs the shared [`bump`](.github/actions/bump) action. It computes the version (breaking → major, `feat` → minor, else patch) and writes the version file and a new CHANGELOG.md section.
3. The [`publish`](.github/actions/publish) action commits `chore(release): vX.Y.Z` under the owner's identity, tags `vX.Y.Z`, pushes with the `RELEASE_KEY` deploy key (the only actor allowed past the `main` ruleset), and creates the GitHub release `vX.Y.Z`.

## Add your own skill

1. Create `skills/<name>/SKILL.md` with frontmatter.
   - `description`: what it does, leading with the use case.
   - `when_to_use`: the phrases you'd actually say, in German and English.
   - Optionally `argument-hint`.
   - Supporting files go next to it. Reference them from the skill via `${CLAUDE_PLUGIN_ROOT}/skills/<name>/…`.
2. Run `claude plugin validate . --strict` and try it with `claude --plugin-dir .`.
3. Open a PR titled `feat: add <name> skill`. Once merged, it reaches every session through the release.

## Add an external skill

External skills are **copied**, never linked live.

1. Copy the upstream skill directory to `external/<name>/`, together with its upstream `LICENSE`. Only permissive licenses are allowed.
2. Add a row to [`external/SOURCES.md`](external/SOURCES.md):
   - upstream repo, path and tracked ref
   - full commit SHA
   - license
   - date
   - **every** change you make to the copy
3. Validate, then open a PR titled `feat: add external <name> skill`.

The monthly drift check compares each row with upstream. When upstream moved on, it opens a PR that applies the upstream diff on top of your documented adaptations.

## Monthly drift check

[`drift-check.yml`](.github/workflows/drift-check.yml) runs on the 1st of each month, and on demand from the Actions tab. Claude ([`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action)) reads the current Claude Code docs and changelog plus upstream external skills. It edits files following [`.github/drift-check.md`](.github/drift-check.md), and the workflow opens a PR under your identity. Nothing is auto-merged.

GitHub pauses scheduled workflows in public repos after 60 days without repository activity. If that happens, re-enable it in the Actions tab.

## Secrets

| Secret | Used by | How |
| --- | --- | --- |
| `RELEASE_KEY` | release, drift-check | Deploy key with write access, the ruleset's only bypass actor. `/std:new-repo` creates it. |
| `CLAUDE_CODE_OAUTH_TOKEN` | drift-check | Run `claude setup-token`, then `gh secret set CLAUDE_CODE_OAUTH_TOKEN`. |
| `ANDROID_*` (4) | Flutter repos' release | Upload keystore for signing, see `std:flutter-build`. |

## Development

```bash
claude plugin validate . --strict
bash hooks/guard.test.sh
python .github/actions/bump/test_bump.py
claude --plugin-dir .          # try the working tree without installing
```

CI runs all of these on every branch push (`validate.yml`, the required check), plus actionlint and the guard test on Windows. `pr.yml` checks PR titles and refuses Claude attribution in commits and PR bodies. Required checks are never jobs that can be skipped, because GitHub counts a skipped job as passed.
