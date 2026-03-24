# Q2 2026 Roadmap: Strategic Feature Analysis

**Date:** 2026-03-24  
**Status:** Planning  
**Author:** Strategic Analysis

---

## Executive Summary

Analysis of 6 high-impact features that would transform MIDI Captain MAX from a "MIDI controller" to a "live performance system." This roadmap prioritizes category-defining features (Setlist Mode, Simulation Mode) alongside friction reducers (Export/Import, Learn Mode, Bulk Edit) to achieve market differentiation against RJM, Morningstar, and Kemper Remote competitors.

**Recommended Q2 Timeline**: 10 weeks to ship 2 category-defining features + 4 friction reducers.

---

## 1. Setlist / Song Mode

**Priority:** P0 - Product Category Shift  
**Effort:** 4-5 weeks  
**Impact:** 🚀 Market Expansion  
**Timing:** Q2 2026

### Strategic Value

This is the **single most obvious missing "pro player" feature**. Competitors like RJM Mastermind and Morningstar MC series win because they think in songs, presets, and setlists, not only in buttons and banks.

**Market Impact:**
- Direct RJM/Morningstar competitor positioning
- Transforms workflow from "button configuration" to "show preparation"
- Sticky feature (once a user programs their setlist, they won't switch)
- Appeals to working musicians (not just studio engineers)

### Core Features

#### Must-Have (Phase 1: 2-3 weeks)
- **Song entries**: Name, notes, duration metadata
- **Bank/page assignment per song**: Which bank activates when song loads
- **Song order for gigs**: Ordered list with drag-to-reorder
- **Next/previous song navigation**: Footswitch-assignable or MIDI-triggerable
- **Song display on screen**: Show current song name prominently

#### Nice-to-Have (Phase 2: 1 week)
- **Per-song labels/colors/default states**: Override button appearance per song
- **Auto-advance**: Option to auto-load next song after timer/MIDI trigger
- **Song grouping/sets**: Organize songs into multiple setlists (rehearsal, gig A, gig B)

#### Premium (Phase 3: 1 week)
- **Performance mode screen**: Dark-stage optimized UI (large text, high contrast)
- **Song notes/lyrics display**: Chords, cues visible on screen
- **BPM tracking**: Display tempo, tap tempo per song

### Technical Architecture

**Firmware (CircuitPython):**
```python
# New data structures
current_song_index = 0
setlist = [
    {"name": "Song 1", "bank": 0, "bpm": 120, "notes": "Start clean"},
    {"name": "Song 2", "bank": 1, "bpm": 140, "notes": "Big intro"}
]

def load_song(index):
    """Switch to song's assigned bank, update display."""
    song = setlist[index]
    switch_to_bank(song["bank"])
    display_song_name(song["name"])
    current_song_index = index
```

**Config Schema:**
```json
{
  "setlist": [
    {
      "name": "Intro Jam",
      "bank": 0,
      "bpm": 120,
      "notes": "Start clean, build to drive on chorus",
      "duration_minutes": 5,
      "default_button_states": {
        "0": true,  // Clean channel on by default
        "3": false
      }
    }
  ],
  "setlist_navigation": {
    "enabled": true,
    "next_button": 9,      // Button 10 advances to next song
    "prev_button": 8,      // Button 9 goes back
    "midi_trigger_cc": 102 // Optional: MIDI CC for DAW sync
  }
}
```

**Editor UI:**
- New "Setlist" tab/panel
- Song list with drag-drop reordering
- Per-song settings panel (bank selector, metadata fields)
- "Load Song" button for live preview/testing
- Export setlist as separate file for backup

### Dependencies

✅ **Already Implemented:**
- Banks/pages system
- Display text rendering
- Button state management

⚠️ **New Requirements:**
- Song navigation state machine
- Per-song config overrides
- Display mode toggle (setup vs performance)

### Market Research Needed

**Questions:**
1. How do RJM Mastermind and Morningstar MC series handle setlists?
2. What's the mental model: song → bank, or song → snapshot, or song → full config?
3. Do users want DAW sync (send PC when song changes)?
4. What metadata is essential vs nice-to-have?

**Competitive Analysis:**
- **RJM Mastermind**: Song mode is core product feature, explicit song list UI
- **Morningstar MC series**: Presets can be organized but not explicitly "setlist"
- **Kemper Remote**: No setlist mode (missed opportunity on their end)

### Risks

- **Scope creep**: Feature could expand indefinitely (lyrics, backing tracks, MIDI clock)
- **Complexity**: May intimidate casual users if not well-designed
- **Testing burden**: Need real-world setlist data to validate workflow

### Success Metrics

- **Adoption**: 40%+ of users create at least one setlist within 30 days
- **Stickiness**: Users with setlists have 3x higher 90-day retention
- **Word-of-mouth**: "Setlist mode" mentioned in 30%+ of user testimonials

---

## 2. Preset/Template Management

**Priority:** P0 - Blocking Issue  
**Effort:** 1 day (export/import), 2 days (templates), 3-4 days (diff/compare)  
**Impact:** ⚠️ Table Stakes  
**Timing:** **This week** (export/import), next sprint (templates)

### Strategic Value

**Table stakes** for professional use. Users won't recommend a product where they fear losing hours of configuration work.

**Market Impact:**
- Reduces setup anxiety (safe to experiment)
- Enables config sharing (community building)
- Foundation for future cloud sync (if ever needed)
- Reduces support burden (users can rollback bad configs)

### Features

#### Phase 1: Export/Import (1 day) - **BLOCKING**

**Editor UI:**
- "File → Export Configuration" menu item
- "File → Import Configuration" menu item
- File format: JSON (human-readable, future-proof)
- Validation on import with clear error messages
- Confirmation dialog before overwriting current config

**Implementation:**
- Tauri file picker dialog (already available)
- Reuse existing `readConfig`/`writeConfig` commands
- Add validation/normalization pass before import

#### Phase 2: Template Library (2 days)

**Built-in Templates:**
- `templates/std10-starter.json` - Basic CC toggle setup
- `templates/helix-4-cable.json` - Line 6 Helix 4CM preset switching
- `templates/quad-cortex-scenes.json` - Neural DSP scene control
- `templates/kemper-rigs.json` - Kemper rig + stomp control
- `templates/ableton-clips.json` - Ableton Live clip launch grid
- `templates/mainstage-patches.json` - Apple MainStage navigation

**Editor UI:**
- "File → Load Template" menu
- Template browser with preview/description
- "Save as Template" for user-created templates

**File Format:**
```json
{
  "name": "Helix 4-Cable Method",
  "description": "Preset switching + stomp control for Line 6 Helix",
  "author": "MIDI Captain Team",
  "device": "std10",
  "target_gear": ["Line 6 Helix Floor", "Line 6 Helix LT"],
  "config": { /* full config here */ }
}
```

#### Phase 3: Diff/Compare (3-4 days)

**Use Case:** "What changed between my working config and this broken one?"

**Editor UI:**
- "File → Compare with..." menu item
- Side-by-side diff view (JSON text or visual button grid)
- Highlight: added (green), removed (red), changed (yellow)
- "Apply changes from right" button for selective merge

**Library:** Use existing JSON diff lib (e.g., `json-diff`, `deep-diff`)

#### Future: Versioning (Not included in Q2)

- Automatic backup on each save (`.midicaptain-backups/` folder)
- Timestamp-based version history
- "Restore from backup" UI
- Cloud sync (Google Drive, Dropbox integration) - **not planned**

### Dependencies

✅ **Already Available:**
- Tauri file system API
- JSON serialization/deserialization
- Config validation engine

⚠️ **New Requirements:**
- Template metadata schema
- Diff visualization component
- User template storage location

### Risks

- **User error**: Importing wrong device config (STD10 config on Mini6)
- **Version compatibility**: Old configs may not load on new firmware
- **File management**: Users lose track of which file is which

**Mitigations:**
- Add device type check on import (show warning if mismatch)
- Add schema version field, auto-migrate on load
- Suggest naming convention (e.g., `my-config-YYYYMMDD.json`)

### Success Metrics

- **Export adoption**: 60%+ of users export at least once within 7 days
- **Template usage**: 30%+ of new users start from a template
- **Support reduction**: 40% fewer "I lost my config" tickets

---

## 3. Faster Editing Workflows

**Priority:** P1 - Friction Reducer  
**Effort:** 3 days (multi-select/bulk), 1 day (duplicate), 2 days (shortcuts)  
**Impact:** 💨 Quality-of-Life  
**Timing:** Next sprint

### Strategic Value

Won't sell the product, but will make it **loved**. Word-of-mouth differentiator ("so much easier than my old controller").

**Market Impact:**
- Reduces human error (bulk operations prevent typos)
- Compounds with complexity (more buttons = more need for shortcuts)
- Competitive advantage over Morningstar's clunky web UI

### Features (Prioritized)

#### 1. Multi-select + Bulk Edit (3 days) - **HIGHEST ROI**

**Use Case:** "Set all buttons to channel 2"

**Editor UI:**
- Shift+click to multi-select buttons
- Ctrl+A to select all
- Selected buttons show blue border/highlight
- Bulk edit panel appears when 2+ selected:
  - Channel dropdown
  - Color picker
  - Mode dropdown
  - "Apply to selected" button

**Implementation:**
- Add `selectedButtons: Set<number>` to component state
- Bulk update via `updateField()` with button index array
- Validation: warn if operation breaks button consistency

#### 2. Duplicate Page/Bank (1 day)

**Use Case:** "Copy my clean bank to create a drive bank, then tweak colors"

**Editor UI:**
- Right-click bank tab → "Duplicate Bank"
- Prompt for new bank name
- New bank created with all buttons copied
- Auto-select new bank for editing

#### 3. Keyboard Shortcuts Everywhere (2 days)

**Current Coverage:**
- ⌘S / Ctrl+S: Save ✅
- ⌘Z / Ctrl+Z: Undo ✅
- ⌘⇧Z / Ctrl+Shift+Z: Redo ✅

**Add:**
- **⌘D / Ctrl+D**: Duplicate selected button(s)
- **⌘E / Ctrl+E**: Export config
- **⌘I / Ctrl+I**: Import config
- **⌘L / Ctrl+L**: Load template
- **⌘F / Ctrl+F**: Search/filter
- **Delete**: Clear selected button(s)
- **1-9, 0**: Quick-select button by number
- **Tab**: Cycle through form fields
- **Esc**: Clear selection

**Implementation:**
- Add global keyboard event handler
- Show shortcuts in tooltips/menus
- "Keyboard Shortcuts" help modal

#### 4. "Make Radio Group" Helper (1 day)

**Use Case:** "Turn buttons 1-4 into a channel selector"

**Editor UI:**
- Select 2+ buttons
- Right-click → "Make Select Group"
- Prompt for group name (e.g., "channel")
- Auto-populate `select_group` field for all
- Auto-set first button as `default_selected: true`
- Auto-set `mode: "select"` for all

#### 5. Search/Filter Commands (2 days)

**Use Case:** "Which buttons send PC messages?"

**Editor UI:**
- Search bar in toolbar
- Filter options:
  - By command type (CC, Note, PC)
  - By channel
  - By color
  - By mode
  - By label (text search)
- Results highlight matching buttons in DeviceLayout
- "Clear filter" button

#### 6. Drag-to-Copy Actions (3 days) - **LOWER PRIORITY**

**Use Case:** "Copy the 'press' action from Button 1 to Button 5"

**Editor UI:**
- Drag handle on each action section
- Drop zone on other buttons
- Shows "Copy action?" tooltip on hover
- Ctrl+drag to copy, plain drag to move

**Implementation:**
- Svelte DnD library (`svelte-dnd-action`)
- Action serialization/deserialization
- Update form state on drop

### Dependencies

✅ **Already Available:**
- Button selection state
- Form update functions
- Validation engine

⚠️ **New Requirements:**
- Bulk update logic
- Keyboard event routing
- Search/filter index

### Risks

- **Undo complexity**: Bulk operations must be atomic (single undo step)
- **Validation burden**: Bulk edits might create invalid configs
- **UI clutter**: Too many shortcuts/options overwhelm

**Mitigations:**
- Group bulk operations in single undo transaction
- Run validation before applying, show preview
- Progressive disclosure (hide advanced features initially)

### Success Metrics

- **Feature adoption**: 70%+ of users use multi-select within 14 days
- **Efficiency gain**: 30% faster average config time (measured in editor)
- **Error reduction**: 50% fewer "I accidentally..." support tickets

---

## 4. Live-State Simulation

**Priority:** P0 - Category Killer  
**Effort:** 2-3 weeks  
**Impact:** 🛡️ Moat Builder  
**Timing:** Q2 2026

### Strategic Value

**No competitor has this well-executed.** This would be a marketing/demo gold mine.

**Market Impact:**
- Eliminates trial-and-error cycle (saves hours per config)
- Makes complex features (conditionals, select groups) less intimidating
- Potential viral marketing (demo video would be shared widely)
- Competitive moat (competitors would take months to copy)

### Core Features

#### Simulation Mode Toggle

**Editor UI:**
- "Enter Simulation Mode" button in toolbar
- Mode indicator (banner/badge)
- "Exit Simulation Mode" to return to editing

**Behavior Change:**
- DeviceLayout becomes interactive (click to press buttons)
- Buttons light up/change color based on simulated state
- MIDI messages appear in a preview panel (not sent to device)
- Bank switches work visually
- Long-press simulation (hold click)

#### Simulated MIDI Input

**Use Case:** Test bidirectional sync, received MIDI conditions

**Editor UI:**
- "Send MIDI" panel with:
  - CC number slider
  - Value slider
  - Channel dropdown
  - "Send" button
- Messages appear as "IN" in MIDI monitor
- Buttons update state based on received values
- Conditionals evaluate against simulated received MIDI

#### State Inspector

**Use Case:** "Why didn't that conditional trigger?"

**Editor UI:**
- Sidebar panel showing:
  - Current button states (on/off)
  - Current keytime indices
  - Received MIDI values (last seen per CC/channel)
  - Encoder position
  - Expression pedal values
- Real-time updates as simulation runs

#### MIDI Message Preview

**Use Case:** "What does this button actually send?"

**Editor UI:**
- MIDI message list panel (like MIDI Monitor)
- Shows generated messages as buttons are clicked
- Highlight multi-command sequences
- Show conditional branches taken (THEN vs ELSE)

#### Behavior Testing

**Scenarios to Simulate:**
- Button press/release → see MIDI output
- Long-press detection → see threshold countdown
- Keytime cycling → see state changes
- Select group conflicts → see mutual exclusion
- Bank switching → see LEDs update
- Conditional logic → see which branch executes

### Technical Architecture

**Implementation Options:**

**Option A: Port Firmware Logic to TypeScript** (Recommended)
- Extract `ButtonState`, `BankManager`, `ConditionEvaluator` to shared lib
- Compile to TypeScript types
- Editor runs same logic as device
- Pro: Guaranteed consistency
- Con: Maintenance burden (sync two codebases)

**Option B: Shadow State Machine in TypeScript**
- Reimplement button state logic in TypeScript
- Mirror firmware behavior
- Pro: Easier editor integration
- Con: Risk of divergence from firmware

**Option C: WASM Build of Firmware**
- Compile CircuitPython logic to WASM
- Run in browser
- Pro: Perfect consistency
- Con: CircuitPython → WASM toolchain doesn't exist

**Recommendation: Option B** (TypeScript shadow state) with extensive tests to ensure parity.

**TypeScript State Engine:**
```typescript
class SimulatedDevice {
  buttons: ButtonState[]
  banks: BankConfig[]
  currentBank: number
  receivedCC: Map<[channel, cc], value>
  
  pressButton(index: number) {
    const button = this.buttons[index]
    const commands = button.press
    
    // Evaluate conditionals
    commands.forEach(cmd => {
      if (cmd.type === 'conditional') {
        const condition = this.evaluateCondition(cmd.if)
        const branch = condition ? cmd.then : cmd.else
        this.executeCommands(branch)
      } else {
        this.executeCommand(cmd)
      }
    })
    
    // Update button state
    button.state = !button.state
    
    // Handle select groups
    if (button.select_group) {
      this.deselectGroup(button.select_group, index)
    }
  }
  
  executeCommand(cmd: MidiCommand): MidiMessage {
    // Generate MIDI message without sending
    return { /* message data */ }
  }
}
```

### Dependencies

✅ **Already Available:**
- DeviceLayout component (button grid)
- MIDI Monitor component
- Form state management

⚠️ **New Requirements:**
- State simulation engine
- MIDI message generator (non-sending)
- Condition evaluator (TypeScript port)

### Risks

- **Complexity**: Large scope, could delay other features
- **Parity**: Simulation diverges from actual device behavior
- **Performance**: Real-time state updates might lag

**Mitigations:**
- Start with simple simulation (button press/release only)
- Add complexity incrementally (conditionals, banks, etc.)
- Extensive test suite comparing simulated vs actual behavior
- Performance profiling early

### Success Metrics

- **Adoption**: 50%+ of users try simulation mode within 14 days
- **Efficiency**: 40% reduction in "test on device" iterations
- **Delight**: 80%+ NPS from users who use simulation
- **Marketing**: Simulation demo video gets 10k+ views

---

## 5. Smarter Profile System

**Priority:** P1 - Network Effects  
**Effort:** 2 days (embedded docs), 3 days (search), 1 week (conflict warnings)  
**Impact:** 📚 Onboarding + Community  
**Timing:** Next sprint

### Strategic Value

The more profiles exist, the more valuable the product. **Network effects** at play.

**Market Impact:**
- Reduces "time to first success" (critical for new users)
- Community contribution opportunity (user-submitted profiles)
- Recurring marketing content ("new profiles added monthly")
- Differentiation: most competitors have static documentation

### Features

#### Phase 1: Embedded Documentation (2 days)

**Current State:** Profile actions are just labels (e.g., "Scene A")

**Enhanced:**
- Tooltip shows what MIDI is sent: "Sends CC 43 value 0 on channel 1"
- Color-coded by message type (CC = blue, PC = purple, Note = green)
- Link to manufacturer docs (if available)
- Warning indicators (e.g., "Requires Helix firmware 3.0+")

**Implementation:**
```typescript
interface ProfileAction {
  label: string
  description: string  // NEW: "Switches to Scene A on Quad Cortex"
  midiSpec: string     // NEW: "CC 43 = 0 (ch 1)"
  docUrl?: string      // NEW: Link to Neural DSP manual
  requires?: string    // NEW: "Firmware 2.0.0+"
}
```

**Editor UI:**
- Tooltip on hover
- Info icon next to action with click-to-expand details
- Help panel with full profile documentation

#### Phase 2: Plain English Search (3 days)

**Use Case:** "I want tap tempo but don't know which CC that is"

**Editor UI:**
- Search bar in profile action selector
- Fuzzy matching on:
  - Action label ("Tap Tempo")
  - Keywords ("delay", "tempo", "bpm")
  - MIDI spec ("CC 64", "PC 5")
  - Synonyms ("snapshot" = "preset" = "scene")
- Results sorted by relevance

**Implementation:**
- Build search index from profile metadata
- Use Fuse.js or similar fuzzy search library
- Pre-index all profiles on editor load

#### Phase 3: Conflict Warnings (1 week)

**Use Case:** "Button 3 and Button 5 both send CC 20 on channel 1. Is that right?"

**Editor Warnings:**
- **CC/Channel overlap**: "Warning: Button 1 and Button 4 both send CC 20 on ch 1"
- **Select group conflicts**: "Warning: Buttons in group 'channel' don't all have mode='select'"
- **Keytime inconsistency**: "Warning: Button 2 has keytimes=3 but only 2 states defined"
- **Profile mismatch**: "Warning: Using Helix profile but channel is set to 2 (Helix expects ch 1)"

**UI:**
- Warning badge on affected buttons
- Validation panel lists all conflicts
- "Auto-fix" button for common issues
- "Ignore warning" checkbox (user knows best)

#### Phase 4: Profile Packs (Ongoing)

**Built-in Packs:**
- `guitar-amp-modelers.json` - Helix, Quad Cortex, Kemper, HX Stomp
- `daws.json` - Ableton, MainStage, Logic, Reaper
- `keyboards.json` - Nord, Korg, Roland
- `lighting.json` - DMX controllers (if applicable)

**Community Packs:**
- GitHub repo for submissions: `midi-captain-profiles`
- Contribution guide with profile schema
- Monthly review + merge of top submissions
- Attribution in UI ("Profile by @username")

**Versioning:**
```json
{
  "name": "Line 6 Helix",
  "version": "1.2.0",
  "updated": "2026-03-15",
  "compatible_firmware": ["3.0", "3.1", "3.5"],
  "author": "MIDI Captain Team",
  "contributors": ["@guitarist123", "@tonetweaker"]
}
```

### Dependencies

✅ **Already Available:**
- Profile system architecture
- Action resolution engine
- UI for action selection

⚠️ **New Requirements:**
- Profile metadata schema
- Search indexing
- Conflict detection rules

### Risks

- **Maintenance burden**: Profiles go stale as target devices update firmware
- **Complexity**: Too many profiles = choice paralysis
- **Quality control**: Community submissions may be inaccurate

**Mitigations:**
- Version profiles with firmware compatibility metadata
- Curate "official" profiles separately from community
- Automated testing: profile actions generate expected MIDI

### Success Metrics

- **Profile usage**: 60%+ of users load at least one profile
- **Community contributions**: 5+ user-submitted profiles per month
- **Documentation value**: 40% reduction in "how do I..." support tickets
- **Conflict detection**: 30% fewer misconfigured buttons detected via warnings

---

## 6. Deeper MIDI Debugging

**Priority:** P1 - Support Burden Reducer  
**Effort:** 2 days (learn mode), 1 day (compare), 3 days (timeline), 1 week (diagnostics)  
**Impact:** 😍 Power User Delight  
**Timing:** Next sprint

### Strategic Value

Reduces support burden AND delights power users. Marketing angle: "only controller with built-in MIDI diagnostics."

**Market Impact:**
- Reduces "it doesn't work" support tickets (users can debug themselves)
- Makes users feel empowered (increases brand loyalty)
- Educational: teaches users about MIDI protocol
- Differentiator: no competitor has this depth

### Features

#### Phase 1: Learn Mode (2 days) - **KILLER FEATURE**

**Use Case:** "What MIDI does my Helix send when I press Snapshot 3?"

**Editor UI:**
- "Learn" button next to each MIDI command field
- Click Learn → editor listens for incoming MIDI
- First received message auto-populates fields:
  - CC number
  - Value
  - Channel
- "Keep listening" mode to capture sequence of messages
- Cancel button to stop learning

**Implementation:**
```typescript
let learningMode = false
let learningCallback: (msg: MidiMessage) => void

function enableLearnMode(fieldPath: string) {
  learningMode = true
  learningCallback = (msg) => {
    // Parse incoming MIDI
    updateField(fieldPath, msg.cc)
    updateField(fieldPath + '.value', msg.value)
    updateField(fieldPath + '.channel', msg.channel)
    learningMode = false
  }
}

// In MIDI Monitor
if (learningMode && midiEvent.direction === 'in') {
  learningCallback(midiEvent)
}
```

**UX Polish:**
- Visual feedback (pulsing "Listening..." indicator)
- Timeout after 30 seconds
- Error handling (no MIDI device connected)

#### Phase 2: Compare Expected vs Received (1 day)

**Use Case:** "My button sends CC 20 = 127, but device received CC 20 = 64. Why?"

**MIDI Monitor Enhancement:**
- Add "Expected" column next to "Actual"
- When button pressed, calculate expected MIDI
- Display side-by-side:
  ```
  Button 3 Pressed
  Expected: CC 20 = 127 (ch 1)
  Received: CC 20 = 64  (ch 1) ⚠️ VALUE MISMATCH
  ```
- Highlight mismatches in red/yellow
- Possible causes shown as hints:
  - "Value mismatch: Check host processing"
  - "Channel mismatch: Check routing"
  - "Never received: Check MIDI connection"

#### Phase 3: Timeline Correlation (3 days)

**Use Case:** "I pressed Button 5 at 12:34:56.789. What MIDI came back?"

**MIDI Monitor Enhancement:**
- Add timeline view (horizontal time axis)
- Button press events marked as vertical lines
- MIDI messages plotted on timeline
- Hover to see details
- Zoom/pan controls
- "Show only events within 500ms of button press" filter

**Visualization:**
```
Timeline
|
12:34:56.500  Button 5 pressed
              ↓ OUT CC 30 = 127 (ch 1)
12:34:56.520  ← IN  CC 30 = 127 (ch 1) ✓ Bidirectional sync working
12:34:57.100  ← IN  PC 5 (ch 1)        ? Unexpected message
```

#### Phase 4: "Why Didn't This Button Light?" Diagnostics (1 week)

**Use Case:** Bidirectional sync isn't working. Button doesn't light up when it should.

**Diagnostic Tool:**
- "Diagnose Button" mode
- Traces bidirectional sync logic:
  1. ✓ Button sends CC 20 = 127
  2. ✓ MIDI message sent over USB
  3. ⚠️ Host received but sent back wrong value (CC 20 = 0)
  4. ✗ Button LED didn't update (received value doesn't match button state)
- Step-by-step explanation with suggestions:
  - "Host sent CC 20 = 0, but button expects 127. Check host configuration."
  - "No incoming MIDI detected. Check MIDI routing in host."

**Implementation:**
- Instrument `handle_midi()` function with debug logging
- Capture state snapshots before/after MIDI events
- Build diagnostic report from logs

#### Phase 5: Export Reproducible Bug Bundle (Follow-up)

**Use Case:** "Something's broken, but I can't explain what."

**Export:**
- Current config (JSON)
- MIDI log (last 1000 messages)
- Button press timeline
- Device state snapshots
- Debug logs
- Firmware version
- Editor version

**Format:** Zip file: `bug-report-20260324-123456.zip`

**Support Workflow:**
1. User exports bug bundle
2. Uploads to GitHub issue or support email
3. Developer imports bundle into editor
4. Replays events in simulation mode
5. Debugs without access to user's physical rig

### Dependencies

✅ **Already Available:**
- MIDI Monitor component
- MIDI event stream
- Config state access

⚠️ **New Requirements:**
- Learn mode UI/UX
- Timeline visualization library
- Diagnostic trace instrumentation

### Risks

- **Complexity**: Timeline/diagnostics could get overwhelming
- **Privacy**: Bug bundles may contain sensitive config data
- **False positives**: Diagnostic suggestions might be wrong

**Mitigations:**
- Progressive disclosure (start simple, add depth later)
- Anonymize user data in bug bundles (optional)
- Label diagnostic hints as "suggestions" not "errors"

### Success Metrics

- **Learn mode adoption**: 50%+ of users try learn mode within 14 days
- **Support reduction**: 50% fewer "MIDI not working" tickets
- **Self-service**: 30% of users resolve issues without contacting support
- **Power user satisfaction**: 90%+ NPS from users who use diagnostics

---

## Overall Strategic Ranking

| Feature | Priority | Effort | Impact | Timing |
|---------|----------|--------|--------|--------|
| **1. Setlist Mode** | P0 | 4-5 weeks | 🚀 Market expansion | Weeks 6-10 |
| **4. Simulation Mode** | P0 | 2-3 weeks | 🛡️ Moat builder | Weeks 3-5 |
| **2. Export/Import** | P0 | 1 day | ⚠️ Blocker | **Week 1** |
| **6. Learn Mode** | P1 | 2 days | 😍 Delight | Week 1 |
| **3. Multi-select/Bulk Edit** | P1 | 3 days | 💨 Friction reducer | Week 2 |
| **5. Profile Docs** | P1 | 2 days | 📚 Onboarding | Week 2 |

---

## Recommended Q2 2026 Roadmap

### Week 1-2: Quick Wins (8 days total)
**Goal:** Ship immediately valuable features that reduce friction

- **Day 1**: Export/import ✅
- **Day 2-3**: Learn mode ✅
- **Day 4-6**: Multi-select + bulk edit ✅
- **Day 7-8**: Profile embedded docs ✅

**Deliverable:** v1.3.0 release with 4 quality-of-life improvements

---

### Week 3-5: Simulation Mode (15 days)
**Goal:** Build competitive moat with unique debugging tool

**Week 3** (Planning + Core Engine):
- Design TypeScript state machine architecture
- Implement `ButtonState` and `BankManager` classes
- Write unit tests for state transitions
- Proof-of-concept: single button press simulation

**Week 4** (UI + Integration):
- Build simulation mode toggle UI
- Integrate state engine with DeviceLayout
- Add MIDI message preview panel
- Implement simulated MIDI input sender
- Test conditional logic evaluation

**Week 5** (Polish + Edge Cases):
- Add state inspector sidebar
- Handle long-press simulation
- Test keytime cycling
- Test select group interactions
- Performance optimization
- Documentation + demo video

**Deliverable:** v1.4.0 release with simulation mode (beta)

---

### Week 6-10: Setlist Mode (25 days)
**Goal:** Transform product into live performance system

**Week 6** (Firmware Foundation):
- Design setlist data structures
- Implement song loading logic
- Add song navigation state machine
- Test bank switching per song

**Week 7** (Firmware Display + Storage):
- Song name display on screen
- Setlist config storage/loading
- Per-song button state overrides
- Integration testing

**Week 8** (Editor UI - Song List):
- New "Setlist" tab in editor
- Song list component (drag-drop reorder)
- Add/remove/rename songs
- Per-song metadata fields
- Bank selector per song

**Week 9** (Editor UI - Integration):
- "Load Song" preview mode
- Setlist export/import
- Validation (check songs reference valid banks)
- Multi-device testing (STD10 + Mini6)

**Week 10** (Polish + Launch):
- Performance mode dark UI
- Song notes/BPM display
- Documentation + user guide
- Demo video + marketing
- Beta test with 10 users
- Bug fixes from feedback

**Deliverable:** v1.5.0 release with setlist mode (GA)

---

## Timeline Summary

```
March 2026
Week 1-2:  Quick Wins (Export, Learn, Bulk Edit, Profile Docs)
           Release: v1.3.0

Week 3-5:  Simulation Mode
           Release: v1.4.0 (beta)

Week 6-10: Setlist Mode
           Release: v1.5.0 (GA)
```

**Total Duration:** 10 weeks (mid-March to end of May 2026)

**Result:** Ship **2 category-defining features** + **4 friction reducers**

---

## What NOT to Do

### ❌ Cloud Sync
**Why:** Premature, complex, recurring costs, not requested by users yet. Can add later if demand exists.

### ❌ Web Editor (WebUSB)
**Why:** 
- WebUSB browser support is inconsistent
- Would fragment codebase (maintain two editors)
- Desktop app is already working well
- Mobile editing not a strong use case for foot controllers

### ❌ Over-engineer Profiles
**Why:** 
- Start simple, let community drive complexity
- Can always add more metadata later
- Risk of choice paralysis with too many options

### ❌ More Button Modes
**Why:**
- Momentary, toggle, select, and tap cover 95% of use cases
- Adding more modes increases cognitive load
- Better to perfect existing modes than add mediocre new ones

### ❌ Plugin/Extension System
**Why:**
- Not requested by users
- Would complicate architecture
- Security/stability risks
- Can revisit in 2027 if community demands it

### ❌ MIDI Thru/Routing
**Why:**
- Niche use case (most users control one device)
- Firmware complexity (UART MIDI is separate from USB)
- Can add later if there's demand

---

## Marketing Angle

Once Setlist + Simulation ship, positioning becomes:

> **"The only MIDI controller that thinks like a live musician"**
> 
> ✅ **Program your setlist, not just your buttons**  
> Test without the rig. Simulate before you gig. Built by musicians who actually perform.
> 
> **vs Competitors:**
> - **RJM Mastermind**: Expensive ($$$), complex steep learning curve
> - **Morningstar MC series**: Powerful but intimidating UI, no simulation
> - **Kemper Remote**: Device-locked, no universal MIDI, no setlist mode
> 
> **MIDI Captain MAX**: The approachable pro tool.

---

## Success Criteria

### User Metrics

**Adoption:**
- 40%+ of users create a setlist within 30 days (signals product-market fit for setlist feature)
- 50%+ of users try simulation mode within 14 days (signals discoverability + value)
- 60%+ of users export config at least once within 7 days (signals trust)

**Retention:**
- Users with setlists have 3x higher 90-day retention
- Users who use simulation have 2x higher satisfaction (NPS 80+)

**Engagement:**
- Average 3 setlists per active user
- Average 12 songs per setlist
- 30% of users contribute or request new device profiles

### Market Metrics

**Competitive:**
- Capture 20% of Morningstar MC6 upgrade market (users seeking easier alternative)
- Become top recommended controller in 5+ guitar forums/subreddits

**Word-of-Mouth:**
- "Setlist mode" mentioned in 30%+ of user testimonials
- "Simulation" mentioned in 40%+ of reviews
- Demo videos get 10k+ views (evidence of viral marketing potential)

### Support Metrics

**Reduction:**
- 40% fewer "I lost my config" tickets (export/import)
- 50% fewer "MIDI not working" tickets (learn mode + diagnostics)
- 30% fewer "How do I..." questions (embedded profile docs)

**Self-Service:**
- 30% of users resolve issues without contacting support
- Documentation page views increase 200% (simulation + setlist guides)

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Simulation diverges from firmware | Medium | High | Extensive test suite, continuous validation |
| Setlist adds 20%+ firmware size | Low | Medium | Profile memory usage, optimize storage |
| Performance issues with large setlists | Low | Medium | Lazy loading, pagination |
| Multi-device config conflicts | Medium | Medium | Device type validation on import |

### Market Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users don't adopt setlists | Low | High | Beta test with gigging musicians, iterate UX |
| Competitors copy features | High | Medium | Focus on execution quality (moat is UX) |
| Scope creep delays shipping | Medium | High | Ruthless prioritization, ship MVP first |
| Features too complex for casual users | Medium | Medium | Progressive disclosure, good defaults |

### Resource Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Profile maintenance burden | High | Medium | Automate testing, community contributions |
| Documentation debt accumulates | High | Medium | Write docs alongside features, not after |
| Testing coverage gaps | Medium | High | Expand test suite incrementally |
| User testing insufficient | Medium | High | Recruit 10-20 beta testers per major feature |

---

## Next Steps

### Immediate (This Week)

1. ✅ **Export/Import** - 1 day
   - Add file picker dialogs
   - Implement import validation
   - Test with corrupted files

2. ✅ **Learn Mode** - 2 days
   - UI for "Learn" button
   - MIDI input listener
   - Auto-populate fields

3. ✅ **Multi-select Bulk Edit** - 3 days
   - Selection state management
   - Bulk edit panel UI
   - Validation for bulk operations

4. ✅ **Profile Docs** - 2 days
   - Add description/midiSpec to profile schema
   - Tooltip component
   - Info panel

**Target:** Ship v1.3.0 by end of Week 2

### Planning (Next Week)

1. **Simulation Mode Architecture**
   - Spike: TypeScript state machine design
   - Decide on state synchronization approach
   - Create technical spec document

2. **Setlist Mode Research**
   - Study RJM Mastermind workflow (buy one? watch videos?)
   - Interview 5 gigging musicians
   - Define MVP scope vs nice-to-have

3. **User Testing Recruitment**
   - Post in guitar forums for beta testers
   - Screen for "active gigging musicians"
   - Set up feedback channels (Discord? GitHub Discussions?)

### Follow-up (Week 3+)

1. Implement simulation mode (Weeks 3-5)
2. Implement setlist mode (Weeks 6-10)
3. Marketing campaign for v1.5.0 launch

---

## Conclusion

This roadmap prioritizes **category-defining features** (Setlist, Simulation) that create competitive moats, alongside **friction reducers** (Export/Import, Learn Mode, Bulk Edit) that improve daily UX.

**Key Insight:** MIDI Captain MAX can't win on hardware (Paint Audio builds that). It must win on **software experience** and **live musician workflow**. Setlist Mode positions the product as a "performance system" not just a "controller." Simulation Mode makes complex features approachable and builds trust.

**10 weeks to ship 2 major features + 4 quality-of-life improvements** is aggressive but achievable with focused execution.

**Market positioning after Q2:** The approachable pro tool that thinks like a live musician.

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-24  
**Status:** Planning - Awaiting approval to begin implementation
