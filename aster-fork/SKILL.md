# Sentinel Rebrand Runbook

## Phase 0: Preflight
- Check environment and dependencies

## Phase 1: Fork
- Clone the upstream repository (`satyajiit/aster-mcp`)
- Set origin to Gitea (`bitonpro/sentinel-mcp`)

## Phase 2-6: Rebrand & UI Injection
- Inject Custom Sentinel Dashboard and Design files from `aster-fork/dashboard` and `aster-fork/design` into `mcp/dashboard`.
- Replace occurrences of `Aster` with `Sentinel` and update package identifiers.

## Phase 7: Build
- Run npm install and build.
