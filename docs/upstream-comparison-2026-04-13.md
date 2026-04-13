# Upstream Comparison Report
**Date:** April 13, 2026  
**Upstream:** MC-Music-Workshop/midi-captain-max  
**Fork:** guisperandio/midi-captain-max  

## Version Status

- **Your fork:** V2.1.0-1 (just pushed Windows device scanning fix)
- **Upstream:** v1.9.0 (latest stable release)

## Major Divergence

The upstream repository has taken a **dramatically different path** than this fork. They have **simplified and stripped down** the project, removing many advanced features, while this fork has **enhanced and extended** functionality.

## Upstream Changes (Since Fork)

### ✅ Worth Considering

#### 1. **Serial Soft-Reboot Improvements** (Multiple commits)
- **Upstream approach:** Ctrl-C + Ctrl-D sequence with timing improvements
  - Ctrl-C (0x03): Interrupt running program
  - 500ms delay for REPL initialization  
  - Ctrl-D (0x04): Soft reload
  - 100ms delay before port close
  - Windows compatibility fixes (drain buffer, send twice)
  
- **Your fork:** Simple Ctrl-R (0x12) approach
  
- **Recommendation:** Consider adopting their more robust Ctrl-C + Ctrl-D sequence. Their extensive testing on Windows found reliability issues that required:
  - Buffer draining after Ctrl-C before sending Ctrl-D
  - Sending each control character twice for Windows reliability
  - Specific timing delays (500ms, then 100ms)

**Commits to review:**
- `c200af4` - Add serial soft-reboot
- `ecdfb65` - Send Ctrl-C and Ctrl-D twice each for Windows
- `b54e409` - Drain serial buffer after Ctrl-C
- `2664c36` - Revert to 500ms timing
- `e9b95fe` - 1000ms REPL delay for Windows

#### 2. **Windows Eject via PowerShell COM** (`3da9688`)
- Uses PowerShell Shell.Application COM object for proper Windows eject
- More reliable than command-line approaches
- Worth reviewing if your Windows eject needs improvement

#### 3. **Serial Port Discovery Deduplication** (`8cbe8b2`)
- Fixes macOS showing duplicate cu.*/tty.* pairs
- Deduplicates by USB serial number, prefers cu.* (non-blocking)
- Your fork may already have this, but worth confirming

#### 4. **New Device Support**
- **ONE** (1-switch variant) - `1c561cc`
- **DUO2** (2-switch variant) - Multiple commits
- If you plan to support these devices, review their pin mappings

#### 5. **CI/CD Improvements**
- Draft releases (`86d123a`) - Test artifacts before publishing
- Parallel job execution (`3e0f507`) - Faster CI
- Artifact action v7 upgrades (`c57855b`, `8f400cd`)
- Cache optimizations for apt (`a857461`) and Rust (`9dc0a1d`)
- Windows NSIS: Install to Program Files by default (`dffbd22`)

#### 6. **Deploy Script Improvements**
- Better progress reporting with rsync itemize prefix stripping (`a67de26`)
- Show current version at deploy start (`90bd81b`)
- Custom drive name handling improvements

### ❌ Already Diverged (Don't Merge)

#### Major Feature Removals in Upstream
The upstream has **removed** these features that your fork has:

1. **Conditional Actions** (PRD Feature 3) - Completely removed
   - If/Then/Else logic
   - Button state conditions
   - MIDI value triggers
   - Expression/encoder conditions

2. **Device Profiles** (PRD Feature 2) - Completely removed
   - Quad Cortex, Helix, Kemper profiles
   - Profile resolver system
   - Action-to-MIDI mapping abstraction

3. **Banks/Pages System** - Completely removed
   - Multi-page configurations
   - Bank switching
   - Button bank assignments

4. **Advanced UI Components** - Completely removed
   - `DeviceLayout.svelte` - Interactive device visualization
   - `DeviceGrid.svelte` - Button grid with indicators
   - `MidiMonitor.svelte` - MIDI traffic monitoring
   - `ProfileSelector.svelte` - Profile management
   - `BanksPanel.svelte` - Bank configuration
   - `ConditionBuilder.svelte` - Conditional logic UI
   - `MidiFlowDiagram.svelte` - Visual MIDI flow

5. **Documentation Removed**
   - `CHANGELOG.md` (415 lines) - Your fork maintains this
   - `CODE_QUALITY_IMPROVEMENTS.md`
   - `FEATURE-ANALYSIS-REPORT.md`
   - All feature PRDs and design docs
   - User guides (EN and PT-BR)

6. **Config Structure Simplification**
   - Flattened config schema
   - Removed multi-command complexity
   - Removed conditional command types
   - Simplified button configuration

#### Code Structure Changes
- Major refactoring: Split `config/mod.rs` into single `config.rs`
- Removed `config/types.rs`, `config/models.rs`, `config/validation.rs`
- Removed MIDI subsystem (`midi.rs` deleted)
- Simplified formStore.ts (750 lines → much smaller)
- Removed device service layer
- Removed profile system entirely

## Architectural Philosophy Difference

### Upstream (v1.9.0)
- **Philosophy:** Simple, focused MIDI controller firmware
- **Target:** Basic MIDI CC/PC/Note mapping with visual feedback
- **Approach:** Minimal feature set, easy to understand and maintain
- **User:** Musicians who want straightforward button-to-MIDI mapping

### Your Fork (V2.1.0)
- **Philosophy:** Advanced, programmable MIDI controller platform
- **Target:** Power users, complex DAW integration, conditional logic
- **Approach:** Feature-rich with conditional actions, profiles, banks
- **User:** Musicians & power users who need programmable, state-aware control

## Recommendations

### 1. Cherry-Pick Serial Reboot Improvements
The Windows reliability fixes are battle-tested and worth adopting:

```bash
# Create a feature branch
git checkout -b feature/improve-serial-reboot

# Cherry-pick the serial reboot commits (may need manual merge)
git cherry-pick c200af4  # Add serial soft-reboot
git cherry-pick b54e409  # Drain buffer
git cherry-pick ecdfb65  # Send twice for Windows
git cherry-pick 2664c36  # Timing fix
```

**Manual integration required** - Your code structure differs, so you'll need to:
1. Replace Ctrl-R (0x12) with Ctrl-C (0x03) + Ctrl-D (0x04) sequence
2. Add 500ms delay after Ctrl-C
3. Add buffer drain before Ctrl-D
4. Implement double-send for Windows
5. Add 100ms delay before port close

### 2. Review Windows Eject Implementation
If you don't have reliable Windows eject:
```bash
git show 3da9688:config-editor/src-tauri/src/commands.rs | less
```

### 3. Consider CI Optimizations
- Draft releases prevent publishing broken builds
- Parallel jobs speed up CI significantly
- Artifact v7 upgrades (Node.js 24 support)

### 4. Monitor for Bug Fixes
Set up upstream as a remote (already done) and periodically check for:
```bash
git fetch upstream
git log --oneline --no-merges upstream/main --grep="fix\|bug"
```

### 5. Do NOT Merge Upstream Main
Your fork has evolved into a different product with advanced features. Merging would:
- Remove all conditional actions (1000+ lines of code)
- Remove device profiles system
- Remove banks/pages
- Break your V2.x architecture
- Lose months of development work

**Recommendation:** Continue as an independent fork with selective cherry-picks.

## Emulator Addition

Upstream added an emulator (`emulator/` directory):
- `build-uf2.py` - Build UF2 firmware images
- `SPIKE-RESULTS.md` - Emulator documentation

This might be useful for testing without hardware. Worth reviewing:
```bash
git show upstream/main:emulator/
```

## Action Items

### High Priority
- [ ] Implement improved serial reboot (Ctrl-C + Ctrl-D with Windows fixes)
- [ ] Review Windows eject implementation
- [ ] Cherry-pick CI draft releases (`86d123a`)

### Medium Priority  
- [ ] Review serial port deduplication for macOS
- [ ] Consider parallel CI jobs for faster builds
- [ ] Check emulator code for testing workflow ideas

### Low Priority
- [ ] Monitor upstream for bug fixes in shared code paths
- [ ] Review deploy script improvements for progress reporting

### Do Not Do
- ❌ Merge upstream/main (would destroy V2.x features)
- ❌ Remove CHANGELOG.md (your fork maintains this)
- ❌ Simplify config schema (your advanced features need it)
- ❌ Remove conditional actions, profiles, or banks

## Conclusion

**Your fork and upstream have fundamentally diverged.** Upstream chose simplicity; you chose power and flexibility. This is a **healthy fork** with a different target audience.

**Continue as an independent project** with selective cherry-picking of bug fixes and infrastructure improvements. Your advanced features (conditional actions, profiles, banks) provide significant value that upstream intentionally removed.

The only real risk is maintaining compatibility with hardware/firmware changes. Monitor upstream for:
- New device support (ONE, DUO2) if you want to support them
- CircuitPython API changes
- Hardware pinout discoveries

**Your V2.x line is a distinct product.** Consider renaming to clarify the difference (e.g., "MIDI Captain MAX Pro" or "MIDI Captain Advanced").
