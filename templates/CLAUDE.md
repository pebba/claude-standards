# CLAUDE.md: <Project>

General conventions (git workflow, PR titles, releases, attribution) come from the `std` plugin (pebba/claude-standards) and are active in every session. Put only what is specific to this repo here; delete sections that stay empty.

Never add Claude attribution (Co-Authored-By, "Generated with Claude Code", session links) to commits, PRs, tags, release notes or CHANGELOG.

## What this is

<2–3 sentences: what the app does, for whom, platform.>

## Commands

<Exact commands; Claude runs these before calling work done.>

- Setup: `<flutter pub get | uv sync>`
- Run: `<flutter run | uv run <app>>`
- Format: `<dart format . | uv run ruff format .>`
- Lint: `<flutter analyze | uv run ruff check .>`
- Test: `<flutter test | uv run pytest>`
- Release build (local): see `/std:flutter-build` or `/std:python-exe-build`

## Layout

- `<dir>/`: <what lives there>

## Hard constraints (never violate)

- <Product or safety rules, e.g. "no network calls except X", "money as integer cents">

## Deviations from the standards

<Only if this repo intentionally differs from the std rules, with the reason. Otherwise delete this section.>

## Release artifacts

- `<app>.apk`, `<app>.aab` | `<app>.exe`. Latest: https://github.com/pebba/<repo>/releases/latest

## Out of scope

- <Things never to build here>
