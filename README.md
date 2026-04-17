[![CI](https://github.com/guisperandio/midi-captain-max/actions/workflows/ci.yml/badge.svg)](https://github.com/guisperandio/midi-captain-max/actions/workflows/ci.yml)

# MIDI Captain MAX Custom Firmware

**Bidirectional, config-driven CircuitPython firmware for Paint Audio MIDI Captain foot controllers.**

Includes a **GUI Config Editor**!

<img width="1403" height="905" alt="image" src="https://github.com/user-attachments/assets/cd6accb4-a47d-42fd-ab44-0682c65e965b" />

## What It Does

This firmware transforms your MIDI Captain into a **bidirectional MIDI controller** where your host software (DAW, plugin host) can control the device's LEDs and display, not just receive button presses.

**Button modes:** Toggle, momentary, select (radio-button groups), and tap tempo visualization. **Long-press** detection for secondary actions.

**Multi-command actions:** Each button event (press, release, long-press, long-release) can send multiple MIDI commands in sequence — change amp channel and delay preset with one footswitch!

[See here for all open features and issues](https://github.com/guisperandio/midi-captain-max/issues).

## Key Features
- 🔄 **Bidirectional MIDI** — Host can update LEDs/display state with value-based scene matching
- � **Banks/Pages System** — Up to 8 banks per device with button/CC/PC switching for complex live setups
- �📺 **Center display** — Shows button names and MIDI info with smart timeout
- ⚡ **Multi-command actions** — Send multiple MIDI messages per button press/release, each with independent channel control- 🧠 **Conditional Actions** — If/Then/Else logic: buttons adapt based on state (other buttons, received MIDI, encoder, expression pedals)- 💾 **Export/Import Configs** — Save and share button configurations as JSON files with ⌘E/⌘I shortcuts
- 🎯 **Device Profiles** — Built-in MIDI mappings for popular devices (Quad Cortex, Helix, Kemper, Ableton, MainStage)
- ⚙️ **Config-driven** — Visual GUI Config Editor for all settings
- 🎨 **Visual feedback** — LEDs and LCD reflect actual host state
- 🔘 **Flexible modes** — Toggle, momentary, select groups, tap tempo with accurate LED visualization
- ⏱️ **Long-press support** — Secondary actions on hold
- 🎛️ **Full input support** — Footswitches, rotary encoder, expression pedals
- 🔁 **Keytimes** — Multi-press cycling through states (like OEM SuperMode)
- 🎸 **Stage-ready** — No unexpected resets, no crashes, no surprises

## Supported Devices

| Device | Status |
|--------|--------|
| MIDI Captain STD10 (10-switch) | ✅ Fully working |
| MIDI Captain Mini6 (6-switch) | ✅ Fully working |
| MIDI Captain Nano4 (4-switch) | ✅ Config validation working |
| MIDI Captain Duo2 (2-switch) | ✅ Config validation working |
| MIDI Captain One1 (1-switch) | ✅ Config validation working |

# Installation

1. [Download the latest firmware.zip and appropriate GUI Config Editor](https://github.com/guisperandio/midi-captain-max/releases/latest)
2. Connect your MIDI Captain via USB (hold Button 1 while powering on)
3. Copy all files and folders from the zip to the device drive (CIRCUITPY or MIDICAPTAIN)
4. On mini6, rename `config-mini6.json` to `config.json`, overwriting the existing one.
5. Power off/on or unplug and replug USB to restart

## Configuration

### Custom USB Drive Name

If you have multiple MIDI Captain devices, you can give each one a unique name! Edit the `usb_drive_name` field in `config.json`:

```json
{
  "device": "std10",
  "usb_drive_name": "MYCAPTAIN",
  ...
}
```

**Requirements:**
- Maximum 11 characters
- Letters, numbers, and underscores only
- Will be automatically converted to uppercase

The name persists across power cycles and USB disconnects. Change it anytime by editing config.json and restarting the device.

### Boot Splash Screen

Customize your device with a boot splash image that displays during startup!

1. Create a **240×240 pixel BMP image** (your logo, band name, etc.)
2. Name it `splash.bmp`
3. Copy it to the root of the device drive
4. Power cycle to see it on boot

**Optional config** (add to `config.json`):
```json
{
  "splash_screen": {
    "enabled": true,
    "duration_ms": 1500,
    "idle_timeout_seconds": 60
  }
}
```

The splash can also act as a **screensaver** — set `idle_timeout_seconds` to show it after inactivity (0 = disabled).

See [firmware/circuitpython/SPLASH_README.md](firmware/circuitpython/SPLASH_README.md) for detailed instructions and design tips. Use the included `tools/generate_splash.py` script to create a simple text-based splash:

```bash
python3 tools/generate_splash.py "MY BAND" "Live Setup"
```

### Config Editor App (Recommended)

The **MIDI Captain MAX Config Editor** is a desktop app that makes configuration easy!

**Download for your platform:**
- **macOS:** `MIDI-Captain-MAX-Config-Editor-[version].dmg`
- **Windows:** `MIDI-Captain-MAX-Config-Editor-[version].msi` or `MIDI-Captain-MAX-Config-Editor-[version]-setup.exe`

Get the latest release from [Releases](https://github.com/guisperandio/midi-captain-max/releases/latest)

### Installation

**MacOS:**
1. Open the DMG and drag the app to your Applications folder

**Windows:**
1. Run the MSI installer or setup.exe
2. At this time, Windows builds are unsigned. Users will see a Windows SmartScreen warning.
3. To continue installation, click "More Info" --> "Run Anyway".
    - Signing certificates will be obtained in the near future.

### Usage

1. Launch the app and connect your MIDI Captain
2. Edit button labels, CC numbers, and colors using the visual editor
3. Configure Device Profiles for quick MIDI setup
4. Save directly to the device — option to safely eject when done
5. Power cycle the device to load the new settings.

# Features

- 🖱️ **Visual editing** — No JSON syntax to learn
- ✅ **Real-time validation** — Catch errors before saving
- 🎨 **Color picker** — Visual color selection
- 🔍 **Device detection** — Automatically detects connected MIDI Captain
- 🎯 **Device Profiles** — Quick setup with built-in MIDI mappings
- 📊 **MIDI Monitor** — Real-time message debugging with filtering, export, and professional monitoring tools
- ⏏️ **Safe eject** — Cleanly ejects device after saving (macOS/Linux)

## Device Profiles

The config editor includes **built-in profiles** for popular music production devices, making setup faster and eliminating MIDI reference lookups.

### Included Profiles

- **Neural DSP Quad Cortex** — Scene select, stomp/preset modes, tuner
- **Line 6 Helix** — Snapshots, stomps, tap tempo, tuner
- **Line 6 HX Stomp** — Snapshots, stomps (compact 6-switch layout)
- **Kemper Profiler** — Rig select, stomp modes, tap tempo, tuner
- **Ableton Live** — Track control, clip launch, scene select, transport
- **Apple MainStage** — Patch select, bypass, tap tempo

### Using Profiles

1. Open a button in the editor
2. Enable "Use Device Profile"
3. Select your device from the dropdown
4. Choose an action (e.g., "Scene A", "Snapshot 1")
5. Assign to Press/Release/Long Press event
6. Optional: Override the MIDI channel

The editor shows a live preview of the MIDI commands that will be sent. You can mix profile actions with custom MIDI commands on the same button!

## Manual Configuration

You can also edit `config.json` directly on the device. The firmware uses an **event-based** format where each button can define multiple commands per action:

```json
{
  "device": "std10",
  "global_channel": 0,
  "usb_drive_name": "MYCAPTAIN",
  "dev_mode": false,
  "buttons": [
    {
      "label": "DELAY",
      "color": "blue",
      "mode": "toggle",
      "off_mode": "dim",
      "channel": 0,
      "press": [
        {"type": "cc", "cc": 20, "value": 127}
      ],
      "release": [
        {"type": "cc", "cc": 20, "value": 0}
      ]
    },
    {
      "label": "DRIVE",
      "color": "orange",
      "mode": "momentary",
      "press": [
        {"type": "cc", "cc": 23, "value": 127},
        {"type": "pc", "program": 5}
      ],
      "release": [
        {"type": "cc", "cc": 23, "value": 0}
      ],
      "long_press": [
        {"type": "cc", "cc": 40, "value": 127, "threshold_ms": 700}
      ],
      "long_release": [
        {"type": "cc", "cc": 40, "value": 0}
      ]
    },
    {
      "label": "CLEAN",
      "color": "green",
      "mode": "select",
      "select_group": "channel",
      "default_selected": true,
      "press": [
        {"type": "pc", "program": 0}
      ]
    },
    {
      "label": "CRCH",
      "color": "red",
      "mode": "select",
      "select_group": "channel",
      "press": [
        {"type": "pc", "program": 1}
      ]
    },
    {
      "label": "TAP",
      "color": "cyan",
      "mode": "momentary",
      "press": [
        {"type": "cc", "cc": 44, "value": 127, "channel": 0},
        {"type": "cc", "cc": 1, "value": 127, "channel": 1}
      ]
    },
    {
      "label": "VERB",
      "color": "blue",
      "mode": "toggle",
      "keytimes": 3,
      "press": [
        {"type": "cc", "cc": 20, "value": 64}
      ],
      "states": [
        {"cc": 20, "value": 64, "color": "blue", "label": "50%"},
        {"cc": 20, "value": 96, "color": "cyan", "label": "75%"},
        {"cc": 20, "value": 127, "color": "white", "label": "100%"}
      ]
    },
    {
      "label": "SMART",
      "color": "purple",
      "mode": "momentary",
      "press": [
        {
          "type": "conditional",
          "if": {"type": "button_state", "button": 0, "state": "on"},
          "then": [
            {"type": "cc", "cc": 30, "value": 127},
            {"type": "pc", "program": 10}
          ],
          "else": [
            {"type": "cc", "cc": 30, "value": 64}
          ]
        }
      ]
    }
  ],
  "encoder": {
    "enabled": true,
    "cc": 11,
    "label": "MOD",
    "min": 0,
    "max": 127,
    "initial": 64,
    "channel": 0,
    "push": {
      "enabled": true,
      "mode": "toggle",
      "label": "PUSH",
      "cc": 14,
      "cc_on": 127,
      "cc_off": 0,
      "channel": 0
    }
  },
  "expression": {
    "exp1": {
      "enabled": true,
      "cc": 12,
      "label": "EXP1",
      "min": 0,
      "max": 127,
      "polarity": "normal",
      "threshold": 2,
      "channel": 0
    }
  },
  "display": {
    "button_text_size": "medium",
    "status_text_size": "medium",
    "expression_text_size": "medium"
  }
}
```

This example demonstrates:
- **Toggle mode** with press/release (Button 1: DELAY)
- **Momentary mode** with long-press/long-release (Button 2: DRIVE)
- **Multi-command actions** sending CC + PC simultaneously (Button 2)
- **Select groups** for radio-button behavior (Buttons 3-4: channel switching)
- **Default selected** button activated on boot (Button 3: CLEAN)
- **Per-command channels** controlling multiple devices (Button 5: TAP)
- **Keytimes** with per-state overrides (Button 6: VERB cycling 3 reverb levels)
- **Conditional actions** with if/then/else logic based on other button states (Button 7: SMART)
- **Encoder** configuration with push button
- **Expression pedal** setup
- **Display** text size settings

### Button Configuration Fields

| Field | Description | Default |
|-------|-------------|---------|
| `label` | Text shown on LCD (max 6 chars) | Button number |
| `color` | Named color: `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `orange`, `purple`, `white` | `white` |
| `mode` | Button behavior: `toggle`, `momentary`, `select`, `tap` | `toggle` |
| `off_mode` | LED when OFF: `dim` (30% brightness) or `off` (completely off) | `dim` |
| `channel` | MIDI channel (0-15) | 0 |
| `select_group` | String ID for radio-button groups (only one ON at a time) | none |
| `keytimes` | Number of states to cycle through (1-99) | 1 |
| `states` | Array of per-state overrides (for keytimes > 1) | `[]` |
| `press` | Array of commands sent on press | `[]` |
| `release` | Array of commands sent on release | `[]` |
| `long_press` | Array of commands sent on long press (with `threshold_ms`) | `[]` |
| `long_release` | Array of commands sent on release after long press | `[]` |
| `long_press_label` | Custom label shown during long press (max 6 chars) | none |
| `long_press_color` | LED color override during long press (any named color) | none |

### Command Object Fields

| Field | Description | Types |
|-------|-------------|-------|
| `type` | Command type | `cc`, `note`, `pc`, `pc_inc`, `pc_dec` |
| `channel` | MIDI channel (0-15, optional - defaults to button or global channel) | All |
| `cc` | CC number (0-127) | `cc` |
| `value` | CC value (0-127) | `cc` |
| `note` | MIDI note (0-127) | `note` |
| `velocity` | Note velocity (0-127) | `note` |
| `program` | Program number (0-127) | `pc` |
| `pc_step` | Step value for increment/decrement | `pc_inc`, `pc_dec` |
| `threshold_ms` | Long-press threshold in milliseconds | `long_press` (first command only) |

**Per-Command Channels:**
Each command can specify its own `channel` (0-15). This enables one button to control multiple devices:

```json
{
  "label": "TAP",
  "press": [
    {"type": "cc", "cc": 44, "value": 127, "channel": 0},  // Tap to amp on ch1
    {"type": "cc", "cc": 1, "value": 127, "channel": 1}    // Tap to delay on ch2
  ]
}
```

If `channel` is omitted, the command uses the button's `channel` field, or falls back to `global_channel` (default 0).

**Mode behaviors:**
- **`toggle`**: Alternates ON/OFF, sends `press` when ON, `release` when OFF
- **`momentary`**: ON while held, sends `press` on press, `release` on release
- **`select`**: Always turns ON (never toggles OFF), use with `select_group`
- **`tap`**: Visual tap tempo, blinks on each press

**One-shot pattern (trigger only):**

To send MIDI **only on press** without any release message, simply omit the `release` field:

```json
{
  "label": "TRIG",
  "color": "red",
  "mode": "momentary",
  "press": [
    {"type": "cc", "cc": 20, "value": 127}
  ]
  // No "release" field = nothing sent on release!
}
```

This works in **any mode**:
- **Momentary mode**: Trigger on press, silent on release (great for drum pads, one-shot samples)
- **Toggle mode**: Action only when turning ON, silent when turning OFF
- **Select mode**: Action only when selecting, silent when deselecting

The firmware checks if a `release` action is configured before sending — if it's empty or missing, the button release is silent.

**Repeat pattern (same message every press):**

To send the **same MIDI message every time** you press the button (not alternating), use **toggle mode** with **identical commands** in both `press` and `release` arrays:

```json
{
  "label": "TAP",
  "color": "green",
  "mode": "toggle",
  "press": [
    {"type": "cc", "cc": 64, "value": 127}
  ],
  "release": [
    {"type": "cc", "cc": 64, "value": 127}  // Same as press!
  ]
}
```

How it works:
- **First press**: Turns button ON, sends `press` commands (CC64=127)
- **Second press**: Turns button OFF, sends `release` commands (also CC64=127)
- **Third press**: Turns button ON, sends `press` commands (CC64=127)
- Result: Same message sent **every time** you press

**Use cases:**
- Tap tempo (send same CC repeatedly for BPM detection)
- Scene advance (increment scene on each press)
- MIDI clock nudge or sync
- Any device expecting repeated triggers of the same value

**Select groups:**
Buttons with the same `select_group` act like radio buttons — selecting one deselects others in the group. Works with both `toggle` and `select` modes.

### Advanced: Keytimes (Multi-Press Cycling)

**Keytimes** allows a button to cycle through multiple states on repeated presses, similar to the OEM SuperMode firmware. Each state can have different MIDI values and LED colors.

#### Example: 3-State Reverb Button

```json
{
  "label": "VERB",
  "color": "blue",
  "mode": "toggle",
  "keytimes": 3,
  "press": [
    {"type": "cc", "cc": 20, "value": 64}
  ],
  "release": [
    {"type": "cc", "cc": 20, "value": 0}
  ],
  "states": [
    {"cc": 20, "value": 64, "color": "blue"},    // State 1: 50% wet
    {"cc": 20, "value": 96, "color": "cyan"},    // State 2: 75% wet
    {"cc": 20, "value": 127, "color": "white"}   // State 3: 100% wet
  ]
}
```

- **First press**: Sends CC20=64, LED shows blue
- **Second press**: Sends CC20=96, LED shows cyan
- **Third press**: Sends CC20=127, LED shows white
- **Fourth press**: Cycles back to state 1

#### Per-State Options

Each state in the `states` array can override command values from the base `press`/`release` arrays:
- `cc`, `value`: CC command overrides
- `note`, `velocity`: Note command overrides
- `program`: PC command override
- `pc_step`: PC inc/dec step override
- `color`: LED color for this state
- `label`: Display label for this state

#### Notes

- Keytimes defaults to 1 (standard single-state behavior)
- Maximum 99 states per button
- Works with toggle, momentary, and select modes
- State overrides apply to the command values in `press`/`release` arrays

### Multi-Command Actions

Each button action can send **multiple MIDI commands in sequence**. This enables complex macros with a single footswitch press.

#### Example: Amp Channel + Delay Preset

```json
{
  "label": "CH2+DLY",
  "color": "red",
  "press": [
    {"type": "cc", "cc": 30, "value": 127},  // Switch to channel 2
    {"type": "pc", "program": 12}             // Load delay preset
  ]
}
```

#### Example: Scene Select with Expression Reset

```json
{
  "label": "SCENE3",
  "color": "purple",
  "press": [
    {"type": "pc", "program": 3},             // Load scene 3
    {"type": "cc", "cc": 12, "value": 64}     // Reset expression to middle
  ]
}
```

### Conditional Actions

Buttons can execute different commands based on **runtime conditions** like other button states, received MIDI values, expression pedal position, or encoder value. This enables intelligent, context-aware behavior.

#### Basic IF/THEN/ELSE Structure

```json
{
  "label": "SMART",
  "color": "purple",
  "press": [
    {
      "type": "conditional",
      "if": {"type": "button_state", "button": 0, "state": "on"},
      "then": [
        {"type": "cc", "cc": 30, "value": 127},
        {"type": "pc", "program": 10}
      ],
      "else": [
        {"type": "cc", "cc": 30, "value": 64}
      ]
    }
  ]
}
```

**Logic**: If Button 0 is ON, send CC30=127 + PC10; otherwise send CC30=64.

#### Condition Types

**1. Button State**
Check if another button is on or off:
```json
{"type": "button_state", "button": 2, "state": "on"}
```

**2. Button Keytime**
Check the current keytime state of a multi-state button:
```json
{"type": "button_keytime", "button": 3, "keytime": 1}
```
*Note: keytime is 0-indexed (0 = first state)*

**3. Received MIDI CC**
Check value of incoming CC messages:
```json
{"type": "received_midi", "channel": 0, "cc": 20, "operator": "gte", "value": 64}
```
**Operators**: `eq`, `ne`, `gt`, `lt`, `gte`, `lte`

**4. Expression Pedal Position**
Check expression pedal value:
```json
{"type": "expression", "pedal": "exp1", "operator": "gt", "value": 100}
```

**5. Encoder Position**
Check rotary encoder value:
```json
{"type": "encoder", "operator": "gte", "value": 64}
```

#### Real-World Examples

**Scene-Aware Boost Button:**
```json
{
  "label": "BOOST",
  "color": "yellow",
  "press": [
    {
      "type": "conditional",
      "if": {"type": "button_state", "button": 0, "state": "on"},
      "then": [{"type": "cc", "cc": 50, "value": 127}],
      "else": [{"type": "cc", "cc": 51, "value": 127}]
    }
  ]
}
```
*If clean channel (button 0) is active, use boost CC50; if drive channel, use boost CC51.*

**Expression-Based Scene Switch:**
```json
{
  "label": "AUTO",
  "color": "blue",
  "press": [
    {
      "type": "conditional",
      "if": {"type": "expression", "pedal": "exp1", "operator": "lt", "value": 30},
      "then": [{"type": "pc", "program": 0}],
      "else": [{"type": "pc", "program": 1}]
    }
  ]
}
```
*Load scene 0 if expression pedal is at heel, scene 1 if at toe.*

**Host-Responsive Button:**
```json
{
  "label": "SYNC",
  "color": "green",
  "press": [
    {
      "type": "conditional",
      "if": {"type": "received_midi", "channel": 0, "cc": 100, "operator": "eq", "value": 127},
      "then": [{"type": "cc", "cc": 25, "value": 127}],
      "else": [{"type": "cc", "cc": 25, "value": 0}]
    }
  ]
}
```
*Button behavior changes based on what the host last sent (bidirectional sync).*

#### Notes

- Conditionals can be mixed with regular MIDI commands in the same action array
- Supports nested logic: THEN/ELSE branches can contain multiple commands
- All operators work with MIDI value range (0-127)
- Conditions are evaluated at button press time using current device state

### Config Validation

Before deploying a config to your device, you can validate it offline using the provided CLI tool:

```bash
python tools/validate_config.py firmware/circuitpython/config.json
```

**Features:**
- **Device-aware validation**: Checks button count matches device type (STD10=10, Mini6=6, etc.)
- **Multi-bank support**: Validates bank switch buttons and all banked configurations
- **Conditional detection**: Recognizes conditional commands in multi-command arrays
- **Encoder/expression defaults**: Matches firmware behavior (enabled: true by default)
- **Batch validation**: `--check-all` mode validates all device templates

**Example output:**
```
✓ Config validation passed for std10
  • Device: std10
  • Buttons: 10
  • Encoder: enabled
  • Expression pedals: exp1, exp2
  • Banks: 0
```

**Error example:**
```
✗ Config validation FAILED
  • Button channel 16 exceeds max (15)
  • Button 11 exceeds device limit for mini6 (6 buttons)
```

The validator uses the same validation logic as the Rust backend, catching config errors **before** you deploy to hardware.

#### Example: Long-Press for Secondary Function

```json
{
  "label": "DELAY",
  "color": "blue",
  "press": [
    {"type": "cc", "cc": 20, "value": 127}    // Short press: delay ON
  ],
  "long_press": [
    {"type": "cc", "cc": 40, "value": 127, "threshold_ms": 700},  // Hold 700ms: tap tempo ON
    {"type": "cc", "cc": 41, "value": 64}     // Reset tap rate
  ],
  "long_release": [
    {"type": "cc", "cc": 40, "value": 0}      // Release: tap tempo OFF
  ]
}
```

## MIDI Protocol

The firmware supports **CC (Control Change)**, **Note On/Off**, and **Program Change** messages. All MIDI mappings are fully configurable via `config.json`.

### Default Device → Host Mappings

These are the default CC numbers (fully customizable):

| Input | MIDI Message |
|-------|--------------|
| Encoder wheel | CC 11 (0-127 position) |
| Encoder push | CC 14 (127=press, 0=release) |
| Footswitch 1-10 | CC 20-29 (127=ON, 0=OFF) |
| Expression 1 | CC 12 (0-127) |
| Expression 2 | CC 13 (0-127) |

### Host → Device (LED/state control)

The device responds to incoming MIDI to update button states. Send CC messages matching your button's configured `press` commands:
- `CC 20, value 127` → Button 1 turns ON (LED lights up)
- `CC 20, value 0` → Button 1 turns OFF (LED off/dim)

**Value-based scene matching:**
The firmware matches incoming CC number, channel, **and value** against button configurations. This enables scene switching on devices like the Quad Cortex:

```json
{
  "label": "SCENE1",
  "press": [{"type": "cc", "cc": 43, "value": 0, "channel": 0}]
},
{
  "label": "SCENE2",
  "press": [{"type": "cc", "cc": 43, "value": 1, "channel": 0}]
},
{
  "label": "SCENE3",
  "press": [{"type": "cc", "cc": 43, "value": 2, "channel": 0}]
}
```

When the Quad Cortex sends `CC 43, value 1, channel 0`, only the SCENE2 button lights up.

## Use Cases

- **Gig Performer / MainStage** — Sync button states with plugin bypass
- **Ableton Live** — Control track mutes/solos with visual feedback
- **Guitar Rig / Helix Native** — Effect on/off with LED confirmation
- **Any MIDI-capable host** — Generic CC control with bidirectional sync

## Repository Layout

| Path | Purpose |
|------|---------|
| `firmware/circuitpython/` | CircuitPython firmware (production-ready) |
| `firmware/rust/` | Rust+Embassy firmware (experimental) |
| `config-editor/` | Desktop config editor app (Tauri + Svelte) |
| `firmware/circuitpython/original_helmut/` | Helmut Keller's original code (reference) |
| `docs/` | Hardware specs, design docs |
| `tools/` | Helper scripts |

## License

Copyright © 2026 Maximilian Cascone. All rights reserved.

You may use this firmware freely for personal or commercial performances. Redistribution of modified versions requires permission. See [LICENSE](LICENSE) for details.

## Attribution

This project builds on work by **Helmut Keller** ([hfrk.de](https://hfrk.de)), whose original firmware demonstrated bidirectional MIDI on the MIDI Captain. His code is preserved in `firmware/original_helmut/` as a reference.

---

## Questions, Comments, Suggestions are welcome

[Open an issue](https://github.com/guisperandio/midi-captain-max/issues) or check [AGENTS.md](AGENTS.md) for developer documentation.
