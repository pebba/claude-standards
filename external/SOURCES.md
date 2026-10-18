# External skills

Skills copied from other repositories live in `external/<skill>/`, next to their upstream `LICENSE`. They are copies, never live links; the monthly drift check (`.github/workflows/drift-check.yml`) compares each row with upstream and opens a PR with the diff when upstream moved on.

| Skill | Upstream repo | Upstream path | Ref | Commit | License | Copied | Own adaptations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _none yet_ | | | | | | | |

Column notes:
- **Upstream repo:** clone URL, e.g. `https://github.com/anthropics/skills`.
- **Upstream path:** the skill directory inside that repo, e.g. `skills/pdf`.
- **Ref:** the branch or tag that is tracked, e.g. `main`.
- **Commit:** the full SHA the copy is based on.
- **License:** SPDX id. Only permissive licenses (MIT, Apache-2.0, BSD).
- **Own adaptations:** every change to the upstream copy, precise enough that an upstream update can be re-applied on top of it, e.g. "description shortened", "removed scripts/ocr.py".
