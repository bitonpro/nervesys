# Sentinel Rebrand Runbook

## Phase 0: Preflight
- Check environment and dependencies (node, pnpm, java)
- Verify disk space

## Phase 1: Fork
- Clone the upstream repository (`satyajiit/aster-mcp`)
- Set upstream to GitHub and origin to Gitea (`bitonpro/sentinel-mcp`)

## Phase 2: Text Rebrand
- Replace occurrences of `Aster` with `Sentinel` across all code files (except `LICENSE` and `node_modules`).
- Replace `aster-mcp` with `@bitonpro/sentinel-mcp`.
- Update repository references to `bitonpro/sentinel-mcp`.
- Update author names to BitOn.Pro.

## Phase 3: License
- Append BitOn.Pro copyright to the existing MIT LICENSE file, preserving the original author's copyright.

## Phase 4: Package Configuration
- Update `mcp/package.json` with the new package name `@bitonpro/sentinel-mcp`, description, author, and bin commands.

## Phase 5: Dashboard Rebrand
- Connect the newly created `dashboard` codebase in this `aster-fork` to the MCP.
- Configure Nuxt UI (`app.config.ts`, `nuxt.config.ts`, `main.css`) to use the BitOn.Pro color palette and branding.

## Phase 6: Android App Rebrand
- Update Android app ID to `pro.biton.sentinel` in `build.gradle.kts`.
- Update app names and add Hebrew (`values-he`) resources.
- Include the new icon, splash screen, and vector assets from the `design` folder.

## Phase 7: Verification
- Search for leftover instances of `aster` or `Aster` in the rebranded files.
- Verify `package.json` names and `applicationId` in Android builds.

## Phase 8: Commit
- Commit changes locally with a descriptive tag (e.g., `sentinel-v1.0.0-rc1`).

## Phase 9: Push
- Await manual confirmation.
- Push the changes to the Gitea repository.

## Phase 10: Build
- Run `./gradlew assembleDebug` to build the test APK for the Sentinel Android app.
