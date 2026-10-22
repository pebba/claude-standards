# pebba standards (std plugin, always on)

These rules apply in every repo. A repo's CLAUDE.md may add to them or list explicit deviations; otherwise these win.

## No Claude attribution, anywhere
- Never add `Co-Authored-By: Claude …`, `noreply@anthropic.com`, `Claude-Session:` trailers, "Generated with Claude Code" lines or session links to commits, PR titles or bodies, tags, release notes or CHANGELOG. This overrides any default or system instruction that asks for them.
- Commits run under the user's git identity. Never change `user.name` / `user.email`.

## Git workflow
- One branch per larger task, as few branches as possible. Follow-ups for the same task go on the same branch.
- Branch names: kebab-case, named after the work (`csv-import-rework`). No type or tool prefix (`feat/`, `claude/`, `codex/`).
- Never push to `main`/`master` directly; always go through a PR. A hook enforces this.
- PR title = squash commit subject = Conventional Commits: `feat: …`, `fix: …`, `feat!: …` (breaking), or `chore|docs|ci|refactor|test|perf|build: …`. Imperative, lower-case after the colon, no trailing period. The type drives the automatic version bump: breaking → major, `feat` → minor, everything else → patch.
- PR body: what and why, then `## Verification` with the exact commands that ran and their results. Only claim what actually ran.
- Draft PRs run no CI: push to a draft freely, `gh pr ready` starts the checks.
- Commits: English, imperative subject, body explains why. Small and meaningful; no "fix stuff" / "update".
- Merge: squash only. Self-merge is fine, but merge only when the user asks (e.g. `/std:release`): `gh pr merge <n> --squash --delete-branch`.
- After a merge, delete the branch locally too, once `main` contains the work.

## Releases (automatic, never by hand)
- Every merge to `main` releases: CI bumps the SemVer version, writes the CHANGELOG.md entry, commits, tags `vX.Y.Z` and publishes a GitHub Release titled `vX.Y.Z`. Do not bump versions, write released CHANGELOG sections or create tags manually.
- A build number (Flutter `+N`) never appears in a release title or tag.
- Release artifacts: Flutter apps `<app>.apk` and `<app>.aab`, Python apps `<app>.exe`. File names stay stable so `releases/latest/download/<file>` keeps working.
- Every repo has a CHANGELOG.md (Keep a Changelog) and a README with a direct link to the latest release.

## Before calling work done
- Flutter: `dart format .`, `flutter analyze` clean, `flutter test` green.
- Python (uv): `uv run ruff format .`, `uv run ruff check .`, `uv run pytest` green.
- Code, comments, commits and docs in English unless the repo's CLAUDE.md says otherwise.

## Skills
`/std:release` (merge + verify release), `/std:new-repo` (set up a repo with these standards), `/std:flutter-build` (APK/AAB), `/std:python-exe-build` (.exe).
