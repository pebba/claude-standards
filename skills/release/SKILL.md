---
name: release
description: Ship the current work. Make sure a PR exists with a Conventional Commits title, wait for green checks, squash-merge it into main, then verify the automatic release (version bump, vX.Y.Z tag, CHANGELOG entry, GitHub Release with APK/AAB/EXE assets).
when_to_use: Use when the user wants to release, ship, publish, merge the PR, cut a new version, or says "mach ein Release", "merge das", "ausliefern", "neue Version". Also use after finishing a task when the user asks to get it onto main.
argument-hint: "[PR number]"
---

# Release

Releases are automatic: every squash merge to `main` triggers the repo's `release` workflow. It bumps the version from the PR title (breaking → major, `feat` → minor, else patch), writes CHANGELOG.md, tags `vX.Y.Z` and publishes a GitHub Release titled `vX.Y.Z`. This skill gets the PR merged correctly and checks the result. Never bump versions, tag or write CHANGELOG entries by hand.

## 1. Find or open the PR

- With an argument, use PR `$ARGUMENTS`. Otherwise run `gh pr view --json number,title,body,state,isDraft,headRefName,mergeable,url` for the current branch.
- If there's no PR:
  1. Make sure the working tree is committed. Never commit to or push `main`.
  2. Run `git push -u origin HEAD`.
  3. Run `gh pr create --title "<type>: <summary>" --body-file <file>`. The body has what/why plus `## Verification` with the exact commands that ran.
- Draft PRs: ask before running `gh pr ready`.

## 2. Check the title, since it decides the version

- The title must match `^(feat|fix|chore|docs|ci|refactor|test|perf|build|style|revert)(\(scope\))?!?: <imperative summary>`, with no trailing period.
- If it doesn't, propose a corrected title and apply it with `gh pr edit <n> --title "..."`.
- Tell the user the resulting bump. Get the current version with `gh release view --json tagName -q .tagName`, or treat it as `v0.0.0` when there's none. Example: "feat → v1.4.0 → v1.5.0".
- The PR body and every commit must be free of Claude attribution (Co-Authored-By: Claude, noreply@anthropic.com, "Generated with Claude Code", session links). Fix that with `gh pr edit` or by rewording the commits before merging.

## 3. Wait for checks

`gh pr checks <n> --watch --fail-fast`. If a check fails, show the failing log (`gh run view <run-id> --log-failed`), fix it on the branch and push, then watch again. Never merge red.

## 4. Merge (squash only)

Invoking this skill counts as the user's go-ahead to merge. If you triggered it on your own, confirm with the user first.

```bash
gh pr merge <n> --squash --delete-branch
```

The squash subject is the PR title. Don't pass `--admin` and don't bypass the rules.

## 5. Verify the release

1. Find the run: `gh run list --workflow release.yml --branch main --limit 1 --json databaseId,status,conclusion,headSha`. It must belong to the merge commit.
2. Watch it with `gh run watch <id> --exit-status`. On failure, show `gh run view <id> --log-failed` and stop. Don't retry blindly.
3. Check the release with `gh release view --json tagName,name,assets,body,url`:
   - `name` equals `tagName` (`vX.Y.Z`), with no `+build` in either.
   - Assets: Flutter needs `<app>.apk` and `<app>.aab`, Python needs `<app>.exe`. Plugin or library repos have none.
   - The body has no Claude attribution.
4. Run `git switch main && git pull --ff-only`. Check that CHANGELOG.md has the new `## [X.Y.Z]` section on top and the version file (pubspec.yaml / pyproject.toml / .claude-plugin/plugin.json) shows `X.Y.Z`.
5. Delete the local branch with `git branch -d <branch>`. Use `-D` only after confirming `main` contains the work, i.e. the merge commit is on `main`.

## 6. Report

Give the user the version, the release URL, the `releases/latest` link and the asset names. Mention anything unusual, such as a debug-signed APK warning in the notes.
