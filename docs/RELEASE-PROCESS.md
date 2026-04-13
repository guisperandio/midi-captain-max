# Release Process

This document outlines the step-by-step process for creating a new release of MIDI Captain MAX.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Push access to the main repository
- All planned changes merged to `main` branch

## Release Workflow Overview

The release process consists of:

1. **CI Build** - Automatically builds all artifacts on code changes
2. **Tagging** - Tag the commit with a version number
3. **Release Creation** - Workflow downloads CI artifacts and creates draft release
4. **Review & Publish** - Manually review and publish the draft

## Step-by-Step Process

### 1. Ensure CI Has Run Successfully

**CRITICAL:** The release workflow requires a successful CI run for the commit you want to release.

CI automatically runs on **every push to main**, including docs-only changes. This ensures all commits are ready for release tagging.

#### Verify CI passed for the latest commit:

```bash
# Get the latest commit SHA
COMMIT=$(git rev-parse HEAD)

# Check for CI runs on this commit
gh run list --commit $COMMIT --workflow=ci.yml --limit 1
```

#### If CI is still running:

```bash
# Watch the latest run
gh run watch
```

#### If CI failed:

Fix the issues, push the fix, and wait for CI to pass before tagging.

### 2. Tag the Release

Once CI passes, tag the commit:

```bash
# For stable releases (appears as "latest" in GitHub)
git tag v2.1.1
git push origin v2.1.1

# For pre-releases (marked as pre-release in GitHub)
git tag v2.2.0-alpha.1   # Alpha release
git tag v2.2.0-beta.1    # Beta release  
git tag v2.2.0-rc.1      # Release candidate
git push origin v2.2.0-alpha.1
```

**Version Format:**
- Stable: `v{major}.{minor}.{patch}` (e.g., `v2.1.0`)
- Pre-release: `v{major}.{minor}.{patch}-{type}.{n}` (e.g., `v2.2.0-alpha.1`)
- Types: `alpha`, `beta`, `rc`

### 3. Monitor Release Workflow

The release workflow automatically starts when you push a tag:

```bash
# Watch the release workflow
gh run watch

# Or view the latest release run
gh run list --workflow=release.yml --limit 1
```

### 4. Review Draft Release

The workflow creates a **DRAFT** release. Find it at:

```bash
# Open releases page
gh release list

# Or open in browser
open https://github.com/guisperandio/midi-captain-max/releases
```

**Verify the draft includes:**
- ✅ Firmware zip: `midicaptain-firmware-{version}.zip`
- ✅ Latest alias: `midi-captain-max-latest.zip`
- ✅ macOS Config Editor: `MIDI-Captain-MAX-Config-Editor-{version}.dmg`
- ✅ Windows MSI Installer: `MIDI-Captain-MAX-Config-Editor-{version}.msi`
- ✅ Windows NSIS Installer: `MIDI-Captain-MAX-Config-Editor-{version}-setup.exe`
- ✅ Release notes generated from template
- ✅ Auto-generated changelog from PRs/commits

### 5. Test Downloaded Artifacts (Optional but Recommended)

```bash
# Download and test locally
gh release download v2.1.1 --dir /tmp/test-release

# Verify zips aren't corrupted
unzip -t /tmp/test-release/midicaptain-firmware-v2.1.1.zip

# Test config editor installers on target platforms
# - macOS: Open .dmg, drag to Applications, test launch
# - Windows: Install .msi or run setup.exe, test launch
```

### 6. Publish the Release

Once verified, publish the draft:

**Via GitHub UI:**
1. Go to [Releases page](https://github.com/guisperandio/midi-captain-max/releases)
2. Click "Edit" on the draft release
3. Review content one final time
4. Click "Publish release"

**Via CLI:**

```bash
gh release edit v2.1.1 --draft=false
```

### 7. Post-Release Tasks

- [ ] Announce release on social media / community channels
- [ ] Update Gumroad product with new download link (uses `latest` alias)
- [ ] Close milestone if using GitHub milestones
- [ ] Update any external documentation referencing download URLs

## Troubleshooting

### "No successful CI run found for commit"

**Cause:** CI didn't complete successfully yet, or the commit is not on main branch

**Solution:**
```bash
# Check if CI is still running
gh run list --commit $(git rev-parse HEAD) --workflow=ci.yml

# If no runs found, ensure you're on main branch
git branch --contains HEAD

# If CI failed, check the logs
gh run view [RUN_ID] --log-failed

# Fix issues, commit, push, and wait for CI to pass
```

### "Config Editor DMG/MSI not found in CI artifacts"

**Cause:** CI build for macOS/Windows may have failed

**Solution:**
```bash
# Check CI build status
gh run view [RUN_ID] --log-failed

# Fix any build issues, push fix, wait for CI, then re-tag
```

### Release workflow fails after tag push

**Solution:** Re-run the failed workflow
```bash
gh run list --workflow=release.yml --limit 1  # Get run ID
gh run rerun [RUN_ID] --failed
```

## CI Workflow Artifacts

The CI workflow (`ci.yml`) produces these artifacts:

| Artifact Name | Description | Used By |
|---------------|-------------|---------|
| `midicaptain-firmware-*` | Firmware zip for CircuitPython devices | Release workflow |
| `config-editor-dmg` | macOS Config Editor (.dmg) | Release workflow |
| `config-editor-msi` | Windows MSI installer | Release workflow |
| `config-editor-nsis` | Windows NSIS setup.exe | Release workflow |
| `config-editor-app` | macOS .app bundle (internal) | Not released |

Artifacts are retained for **90 days** in GitHub Actions.

## Version Numbering

We follow Semantic Versioning (SemVer):

- **MAJOR** (v2.0.0 → v3.0.0): Breaking changes, incompatible API changes
- **MINOR** (v2.1.0 → v2.2.0): New features, backward compatible
- **PATCH** (v2.1.0 → v2.1.1): Bug fixes, backward compatible

Pre-release identifiers:
- **alpha**: Early testing, expect bugs
- **beta**: Feature complete, final testing
- **rc**: Release candidate, production-ready if no issues found

## Quick Reference

```bash
# Common release commands cheat sheet

# Check if CI passed for current commit
gh run list --commit $(git rev-parse HEAD) --workflow=ci.yml

# Trigger CI manually
gh workflow run ci.yml --ref main

# Watch CI progress
gh run watch

# Tag and release
git tag v2.1.1
git push origin v2.1.1

# Watch release workflow
gh run watch

# List releases
gh release list

# Publish draft release
gh release edit v2.1.1 --draft=false

# Delete a bad tag (before CI completes)
git tag -d v2.1.1
git push origin :refs/tags/v2.1.1
```

## Notes

- **Draft releases** give you time to test artifacts before making them public
- **Latest release** badge/link in GitHub automatically points to the newest non-prerelease
- The `midi-captain-max-latest.zip` alias provides a stable URL for external download links (e.g., Gumroad)
- Release notes are generated from `tools/release_notes.md` template + auto-generated changelog
