#!/usr/bin/env bash
# std PreToolUse guard for Bash/PowerShell tool calls. Exit 2 = deny; stderr is shown to Claude as the reason.
# Blocks direct pushes to main/master and Claude attribution in commits, tags, PRs and releases.
# Greps the raw hook JSON instead of using jq, which Git Bash on Windows doesn't ship.

input=$(cat)
deny() { echo "std guard: $1" >&2; exit 2; }

# First JSON string value for key $1, with \" and \\ unescaped.
field() {
  printf '%s' "$input" | grep -oE "\"$1\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*\"" | head -n1 |
    sed -E "s/^\"$1\"[[:space:]]*:[[:space:]]*\"//; s/\"\$//; s/\\\\\"/\"/g; s/\\\\\\\\/\\\\/g"
}

# Escaped newlines (\n) separate commands just like ';'.
cmd=$(field command | sed 's/\\n/;/g')
[ -n "$cmd" ] || exit 0

attr_target='git[^;]*[[:space:]](commit|tag|notes)|gh[[:space:]]+(pr|release)[[:space:]]+(create|edit|merge|comment)'
attr='co-authored-by:[^;]*(claude|anthropic)|noreply@anthropic\.com|generated with \[?claude|claude-session:'
if grep -Eq "$attr_target" <<<"$cmd" && grep -Eiq "$attr" <<<"$cmd"; then
  deny "Claude attribution (Co-Authored-By: Claude, noreply@anthropic.com, 'Generated with Claude Code', Claude-Session) is not allowed in commits, tags, PRs or releases. Remove it and retry."
fi

push_re='(^|[[:space:]])git([[:space:]]+-[Cc][[:space:]]+[^[:space:]]+|[[:space:]]+-[^[:space:]]+)*[[:space:]]+push([[:space:]]|$)'
main_re="[[:space:]:+/\"'](main|master)([\"'[:space:]]|\$)"
block_msg="Direct pushes to main/master are blocked by the std standards. Push a branch and open a PR (gh pr create) instead."

cwd=$(field cwd)
branch=$(git -C "${cwd:-.}" branch --show-current 2>/dev/null)

# A brand-new repo's very first push has no PR base, so it may create main. ls-remote exit 2 = ref doesn't exist.
first_push() { git -C "${cwd:-.}" ls-remote --exit-code --heads "$1" "$2" >/dev/null 2>&1; [ $? -eq 2 ]; }

while IFS= read -r seg; do
  [[ $seg =~ $push_re ]] || continue
  args=${seg#*push}
  set -f
  pos=()
  for w in $args; do w=${w//[\"\']/}; [[ $w == -* ]] || pos+=("$w"); done
  set +f
  remote=${pos[0]:-origin}

  # Explicit refspec: main, HEAD:main, +main, refs/heads/master, ...
  if [[ $args =~ $main_re ]]; then
    first_push "$remote" "${BASH_REMATCH[1]}" || deny "$block_msg"
  fi

  # No refspec (or HEAD) while on main pushes main.
  if [[ $branch == main || $branch == master ]] && [[ $args != *--tags* && $args != *--delete* ]]; then
    implicit=$(( ${#pos[@]} <= 1 ))
    for p in "${pos[@]:1}"; do [[ $p == HEAD ]] && implicit=1; done
    if (( implicit )); then first_push "$remote" "$branch" || deny "$block_msg"; fi
  fi
done < <(sed -E 's/(&&|\|\||[;|&])/\n/g' <<<"$cmd")

exit 0
