# MIDI Captain MAX
# Product Requirements Document

## Overview

MIDI Captain MAX has evolved from a firmware replacement into a **programmable controller platform**.

We've moved beyond OEM parity to provide a programmable MIDI control environment with advanced features like conditional logic, device profiles, and multi-bank configurations.

Core features:

1. Visual Button Editor ✅ **Completed** (PR #10)
2. Device Profiles ✅ **Completed** (PR #15)
3. Conditional / Smart Actions ✅ **Completed** (PR #28)

---

# Feature 1 — Visual Button Editor ✅

**Status:** Completed in PR #10  
**Implementation:** DeviceLayout component with interactive button grid

## Summary

Replace the current form-based configuration UI with a visual representation of the MIDI Captain hardware.

Users interact directly with buttons on a graphical layout.

## Example Layout

Device Layout

[1] [2] [3] [4] [5]
[6] [7] [8] [9] [10]

Button Settings Panel

- Label
- Color
- Action
- LED behavior
- Advanced options

## Requirements

- Buttons rendered in hardware layout
- Click button to edit
- Selected button highlighted
- Immediate visual feedback

## Acceptance Criteria

- Users configure buttons visually
- Layout matches hardware
- Labels and colors visible

---

# Feature 2 — Device Profiles ✅

**Status:** Completed in PR #15  
**Implementation:** ProfileSelector component + 6 built-in profiles  
**Documentation:** [device-profiles.md](device-profiles.md), [device-profiles-schemas.md](device-profiles-schemas.md)

## Summary

Device profiles convert high-level musician actions into MIDI commands.

Example:

Device: Quad Cortex
Action: Scene B

Resolved MIDI:

CC 43 Value 1

## Profile Types

**Fixed Profiles** — Hardware-specific, no customization
- Neural DSP Quad Cortex
- Line 6 Helix
- Line 6 HX Stomp
- Kemper Profiler

**Template Profiles** — Starting points for customization
- Ableton Live
- Apple MainStage

## Implementation Details

✅ 6 profiles included covering major platforms  
✅ Full `pc_inc`/`pc_dec` support for patch navigation  
✅ Channel override per action  
✅ Per-event assignment (Press/Release/Long Press/Long Release)  
✅ State-specific profile support for keytimes  
✅ Auto-detection badges when profile matches existing commands  
✅ MIDI preview showing resolved commands before save  

---

# Editor Integration ✅

Profiles should appear as a layer above raw MIDI configuration.

Each action supports two sources:

Source:

- Profile Action
- Custom MIDI

Example UI:

Action Source
[ Profile ▼ ]

Device Profile
[ Quad Cortex ▼ ]

Action
[ Scene B ▼ ]

Resolved MIDI
CC 43 • Value 1 • Channel 1

If Custom MIDI is selected:

Type
CC

Channel
1

Controller
43

Value
1

---

# Feature 3 — Conditional Actions ✅

**Status:** Completed in PR #28 (merged 2026-03-23)  
**Implementation:** ConditionEvaluator firmware class + ConditionBuilder/ConditionalCommandBlock UI components  
**Documentation:** Types in `types.ts`, tests in `test_condition_evaluator.py` (15 tests)  

## Summary

Buttons can change behavior depending on state.

Example:

IF drive_active
send CC20 value 0

ELSE
send CC20 value 127

## Requirements

- conditional evaluation engine
- access to button state
- nested conditions

## Acceptance Criteria

- conditional actions execute reliably
- works with multi-command actions
