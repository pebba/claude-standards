#!/usr/bin/env bash
# Runnable check for guard.sh: bash hooks/guard.test.sh (exits non-zero on any failure).
cd "$(dirname "$0")" || exit 1
fail=0
tmp=$(mktemp -d)
g() { git -c user.name=t -c user.email=t@t -c init.defaultBranch=main "$@" >/dev/null 2>&1; }

g init "$tmp/main" && g -C "$tmp/main" commit --allow-empty -m init
g init "$tmp/feature" && g -C "$tmp/feature" commit --allow-empty -m init && g -C "$tmp/feature" switch -c csv-import
g init --bare "$tmp/remote.git"
g init "$tmp/fresh" && g -C "$tmp/fresh" commit --allow-empty -m init && g -C "$tmp/fresh" remote add origin "$tmp/remote.git"

# Claude Code sends native paths; on Windows that means escaped backslashes in the JSON.
jpath() { if command -v cygpath >/dev/null; then cygpath -w "$1" | sed 's/\\/\\\\/g'; else printf '%s' "$1"; fi; }

# check <expected exit> <repo dir> <JSON-escaped command> [tool]
check() {
  local json got
  json=$(printf '{"session_id":"t","cwd":"%s","hook_event_name":"PreToolUse","tool_name":"%s","tool_input":{"command":"%s","description":"push to main"}}' \
    "$(jpath "$tmp/$2")" "${4:-Bash}" "$3")
  bash guard.sh <<<"$json" 2>/dev/null
  got=$?
  if [ "$got" != "$1" ]; then echo "FAIL (got $got, want $1) [$2] $3"; fail=1; fi
}

check 2 feature 'git push origin main'
check 2 feature 'git push -u origin HEAD:main'
check 2 feature 'git push --force origin +main'
check 2 feature 'git -C x push origin refs/heads/master'
check 2 feature 'cd foo && git push origin \"main\"'
check 2 feature 'git push origin main' PowerShell
check 2 main 'git push'
check 2 main 'git push -u origin'
check 2 main 'git push origin HEAD'
check 2 main 'npm test; git push'
check 0 feature 'git push'
check 0 feature 'git push -u origin csv-import'
check 0 main 'git push origin feature-main'
check 0 main 'git push origin main-fix:main-fix'
check 0 main 'git push --tags'
check 0 feature 'git commit -m \"docs: explain why we never push to main\"'
check 0 feature 'git log --oneline main'
check 0 fresh 'git push -u origin main'
check 2 feature 'git commit -m \"feat: x\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\"'
check 2 feature 'gh pr create --title \"feat: x\" --body \"Generated with [Claude Code](https://claude.com/claude-code)\"'
check 2 feature 'git tag -a v1.0.0 -m \"Claude-Session: https://claude.ai/code/abc\"'
check 0 feature 'git commit -m \"feat: add claude settings template\"'
check 0 feature 'ls -la'

rm -rf "$tmp"
[ "$fail" = 0 ] && echo "guard: all checks passed"
exit "$fail"
