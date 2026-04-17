# MIDI Captain MAX - Config Editor User Guide

**Version:** 1.0  
**Language:** English

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Main Interface](#main-interface)
4. [Device Settings](#device-settings)
5. [Banks/Pages System](#banksPages-system)
6. [Button Configuration](#button-configuration)
7. [Device Profiles](#device-profiles)
8. [Conditional Actions](#conditional-actions)
9. [Multi-State Buttons (Keytimes)](#multi-state-buttons-keytimes)
10. [Encoder Configuration](#encoder-configuration)
11. [Expression Pedals](#expression-pedals)
12. [Display Settings](#display-settings)
13. [MIDI Monitor](#midi-monitor)
14. [Keyboard Shortcuts](#keyboard-shortcuts)
15. [Tips and Best Practices](#tips-and-best-practices)
16. [Troubleshooting](#troubleshooting)

---

## Introduction

The **MIDI Captain MAX Config Editor** is a desktop application that allows you to customize your Paint Audio MIDI Captain foot controller (STD10 or Mini6 models). With this editor, you can:

- Configure button labels, colors, and MIDI commands
- Set up complex multi-command actions
- Use device profiles for popular gear (Quad Cortex, Helix, Kemper, etc.)
- Create conditional logic for context-aware button behavior
- Configure encoders and expression pedals
- Customize the device display
- Debug MIDI traffic with the built-in MIDI Monitor
- Work in development or performance mode

---

## Getting Started

### Connecting Your Device

1. **Connect** your MIDI Captain to your computer via USB
2. **Enable USB Drive Mode** (if not in dev mode):
   - Power off the device
   - Hold **Switch 1** (top-left button)
   - Power on while holding Switch 1
   - Release when the USB drive appears
3. The editor will automatically detect your device

### First Launch

When you launch the editor:

1. Your connected device(s) will appear in the **device dropdown** at the top
2. Select your device to load its current configuration
3. The device layout will appear showing all buttons
4. Any unsaved changes will be marked with a yellow dot indicator

---

## Main Interface

The editor is divided into three main areas:

### Left Panel - Device Overview

- **Device Layout**: Interactive visual representation of your foot controller
  - Click any button to select it for editing
  - Button colors and labels reflect current configuration
  - Multi-command buttons show badge indicators
  - LED preview shows button appearance
- **Device Grid** (optional view): List-style view of all buttons
- **Status Bar**: Shows save status and validation errors

### Center Panel - Button Settings

Detailed configuration for the selected button:

- **Button ID & Label**: Identify and name your button
- **Color**: Choose LED color from preset palette
- **Behavior**: Configure mode and channel settings
- **Actions**: Set up MIDI commands for different events
- **State Overrides**: Configure multi-state behavior (keytimes)
- **Advanced Settings**: Select groups, off mode, dim brightness

### Right Side - Global Settings

- Device type and general settings
- USB drive name
- Development mode toggle
- Display text size settings

### Toolbar

- **Undo/Redo**: Navigate configuration history (⌘Z / ⌘⇧Z)
- **View JSON**: Inspect raw configuration
- **Save**: Write changes to device (⌘S)
- **Reload**: Discard changes and reload from device
- **Reset**: Restore factory default configuration

---

## Device Settings

### Device Type

Select your hardware model:
- **STD10**: 10-button foot controller with encoder
- **Mini6**: 6-button compact controller

### Global MIDI Channel

Default MIDI channel for all buttons (1-16). Individual buttons can override this.

### USB Drive Name

Customize the volume name when USB drive mode is enabled:
- Maximum 11 characters
- Only letters, numbers, and underscores
- Automatically converted to uppercase

**Example**: `MIDICAPTAIN`, `MYCONTROL`, `FOOT_SW_01`

### Development Mode

- **OFF** (Performance Mode): USB drive hidden by default. Hold Switch 1 during power-on to enable temporarily.
- **ON** (Dev Mode): USB drive always mounts automatically. Useful during configuration but may impact boot time.

---

## Banks/Pages System

The **Banks/Pages System** allows you to store up to 8 complete button configurations and switch between them instantly on your device. This is essential for complex live setups requiring access to 40-80 button configurations across multiple songs or scenes.

### Overview

**What are Banks?**
- Each bank is a complete set of button configurations (labels, colors, MIDI commands)
- Your device can store up to 8 banks
- Switch between banks without reconnecting to your computer
- Each bank maintains its own button states independently

**Common Use Cases:**
- **Song Sections**: Bank 1 = Intro, Bank 2 = Verse, Bank 3 = Chorus, etc.
- **Multiple Songs**: Each bank represents a different song
- **Preset Layers**: Bank 1 = Rhythm tones, Bank 2 = Lead tones, Bank 3 = Effects
- **Different Devices**: Bank 1 = Amp control, Bank 2 = Effects control, Bank 3 = DAW control

### Managing Banks

The **Banks Panel** (in the Buttons tab) provides tabbed access to all your banks:

#### Adding a Bank
1. Click the **+ Add Bank** button
2. A new bank appears with default button configurations
3. Bank is automatically named "Bank N" (customizable)
4. Maximum 8 banks per device

#### Duplicating a Bank
1. Select the bank you want to copy
2. Click the **Duplicate** button
3. A copy is created with " (Copy)" appended to the name
4. Useful for creating variations of existing setups

#### Renaming a Bank
1. Click the bank name to edit
2. Enter new name (max 20 characters)
3. Press Enter or click away to save
4. Names appear on device display during bank switch

#### Deleting a Bank
1. Click the **Delete** button on the bank tab
2. Confirm deletion
3. Cannot delete if only one bank remains
4. Deleted bank configurations are not recoverable

#### Editing Bank Buttons
1. Click a bank tab to make it active
2. All button editing applies to the active bank
3. Device layout shows active bank's button configuration
4. Switch between banks while editing to configure each one

### Bank Switching Methods

Choose how to switch between banks on your device:

#### Method 1: Button Switching

**Single Button (Cycling)**
- Press one button to cycle through banks in order
- Wraps around: Bank 8 → Bank 1
- Simple and intuitive for sequential navigation

**Configuration:**
1. Select "Button" as switching method
2. Choose button number (1-10 for footswitches, 11 for encoder push on STD10)
3. Each press advances to next bank

**Dual Button (Up/Down)**
- Use two buttons: one for next bank, one for previous
- More control for non-sequential navigation
- Recommended for setups with 4+ banks

**Configuration:**
1. Select "Button" as switching method
2. Click "Switch to Two Buttons (Up/Down)"
3. Set Bank Up button (e.g., button 10)
4. Set Bank Down button (e.g., button 9)

**Important:** Buttons assigned to bank switching cannot be used for regular MIDI commands.

#### Method 2: MIDI CC Switching

Switch banks via incoming MIDI Control Change messages:
- External controller sends CC message
- CC value maps directly to bank index
- Value 0 → Bank 1, Value 1 → Bank 2, etc.

**Configuration:**
1. Select "CC" as switching method
2. Set CC number (0-127)
3. Set MIDI channel (0-15 in config, displayed as 1-16)

**Example:**  
Configure CC 80 on Channel 1. When your DAW or controller sends `CC 80 = 2` on Channel 1, device switches to Bank 3.

#### Method 3: MIDI PC Switching

Switch banks via incoming MIDI Program Change messages:
- Similar to CC but uses Program Change messages
- Configure base PC number (e.g., PC 0)
- PC values offset from base map to banks

**Configuration:**
1. Select "PC" as switching method
2. Set base PC number (0-127)
3. Set MIDI channel (0-15 in config, displayed as 1-16)

**Example:**  
Base PC = 10. PC messages map as follows:
- PC 10 → Bank 1
- PC 11 → Bank 2
- PC 12 → Bank 3

### Bank Switching Behavior

**Visual Feedback:**
- All button LEDs flash briefly in their configured colors
- Bank name appears on center display
- Status shows "Bank N/Total" (e.g., "Bank 2/4")

**State Persistence:**
- Each bank remembers its button states independently
- Switching away and back preserves state
- Useful for maintaining separate scenes

**Cooldown Protection:**
- 200ms minimum delay between bank switches
- Prevents accidental rapid switching
- Ensures clean state transitions

**Instant Transition:**
- Switching completes in under 100ms
- No interruption to performance
- New bank buttons immediately responsive

### Migration from Single-Bank Configs

Existing configurations automatically migrate to the Banks system:
- Your current buttons become "Bank 1"
- No manual migration required
- Original config preserved and functional
- Add more banks when ready

### Example Setups

**Live Band Setup (4 Banks):**
- Bank 1: Song A (verse, chorus, bridge scenes)
- Bank 2: Song B
- Bank 3: Song C
- Bank 4: Song D
- Use dual buttons (9 = prev, 10 = next) to navigate

**Studio Recording Setup (3 Banks):**
- Bank 1: Track arming and input monitoring
- Bank 2: Transport control and markers
- Bank 3: Mix automation and effects
- Use MIDI CC from DAW to switch banks automatically

**Multi-Device Setup (2 Banks):**
- Bank 1: Amp channel switching and reverb
- Bank 2: Stomp pedals on/off and delay time
- Use single button cycling to toggle between devices

---

## Button Configuration

### Button Identity

**Button ID**  
Unique identifier for referencing this button (e.g., `btn1`, `scene_a`)

**Label**  
Display name shown on device screen (max 6 characters)

**Color**  
LED color from preset palette:
- Red, Green, Blue
- Yellow, Cyan, Magenta
- Orange, Purple, White

### Behavior Settings

#### Mode

- **Toggle**: Button alternates between ON and OFF states
  - Press → turns ON, sends Press commands
  - Press again → turns OFF, sends Release commands
  - LED stays lit when ON

- **Momentary**: Button is ON only while held
  - Press → turns ON, sends Press commands
  - Release → turns OFF, sends Release commands
  - Like a sustain pedal

- **Select**: Button turns ON when pressed, stays ON
  - Used with select groups for radio-button behavior
  - Press → turns ON, sends Press commands
  - Other buttons in same group turn OFF automatically

- **Tap**: Advanced mode for tap tempo (future feature)

#### Off Mode

Controls LED appearance when button is OFF:
- **Dim**: LED visible at reduced brightness (configurable %)
- **Off**: LED completely dark

#### Dim Brightness

When Off Mode is "Dim", set the brightness percentage (0-100%):
- **0%**: Completely off
- **15%**: Default subtle glow
- **50%**: Half brightness
- **100%**: Full brightness (appears always on)

Real-time preview shows the dimmed color next to the slider.

#### Select Group

Group multiple buttons for radio-button behavior:
- Assign same group name to related buttons
- When one button turns ON, others in group turn OFF
- Deselected buttons send their Release commands
- Useful for: scene selection, mode switching

**Example**: Group buttons 1-4 as `"scenes"`. Pressing button 2 turns OFF buttons 1, 3, and 4.

#### Default Selected

Mark this button to activate on device startup:
- Button turns ON when device boots
- Sends Press commands at startup
- Only one button per select group should be default

### Channel Override

Override global MIDI channel for this button (1-16). Leave blank to use global channel.

---

## Actions (MIDI Commands)

Each button can send different MIDI commands for four events:

### Event Types

1. **Press**: Sent when button is pressed
2. **Release**: Sent when button is released (or toggled OFF)
3. **Long Press**: Sent when button is held beyond threshold
4. **Long Release**: Sent when button is released after long press

### Action Sources

#### Profile Action (Recommended)

Use built-in profiles for common devices:
- Select device profile (Quad Cortex, Helix, Kemper, etc.)
- Choose action from dropdown
- MIDI commands auto-configured
- Preview shows resolved MIDI

See [Device Profiles](#device-profiles) section for details.

#### Custom MIDI

Configure MIDI commands manually:

**Multiple Commands Per Event**  
Each event (Press, Release, etc.) can send multiple MIDI commands in sequence.

Click **+ Add Command** to add more commands to an event.

### Command Types

#### Control Change (CC)

Most common MIDI message type.

**Parameters:**
- **Type**: CC
- **Controller**: CC number (0-127)
- **Value**: CC value (0-127)
- **Channel**: MIDI channel (1-16, optional)

**Example**: Send CC 20 with value 127 on channel 1

**Common Uses:**
- Toggle effects (value 127 = on, 0 = off)
- Control parameters (0-127 range)
- Switch scenes/snapshots

#### Note On/Off (Note)

Send MIDI note messages.

**Parameters:**
- **Type**: Note
- **Note**: MIDI note number (0-127)
- **Velocity**: Note velocity (0-127)
- **Channel**: MIDI channel (1-16, optional)

**Note**: Velocity 0 = Note Off, Velocity > 0 = Note On

**Common Uses:**
- Trigger drum pads
- Toggle tuner (some devices)
- Trigger samples

#### Program Change (PC)

Change presets/patches.

**Parameters:**
- **Type**: PC
- **Program**: Program number (0-127)
- **Channel**: MIDI channel (1-16, optional)

**Common Uses:**
- Switch presets
- Change patches
- Select banks

#### Program Change Inc (PC+)

Increment program number by step value.

**Parameters:**
- **Type**: PC Inc
- **Step**: Increment amount (default 1)
- **Channel**: MIDI channel (1-16, optional)

**Common Use**: Next preset/patch button

#### Program Change Dec (PC-)

Decrement program number by step value.

**Parameters:**
- **Type**: PC Dec
- **Step**: Decrement amount (default 1)
- **Channel**: MIDI channel (1-16, optional)

**Common Use**: Previous preset/patch button

### Long Press Threshold

For Long Press commands, set the hold duration in milliseconds:
- Default: **500ms** (half second)
- Range: 100-5000ms
- Only applies to first Long Press command

**Example**: Set 1000ms to require 1-second hold before triggering

### Flash Duration (PC Commands)

For Program Change buttons with no persistent state:
- Set LED flash duration in milliseconds
- Default: **200ms**
- Provides visual feedback for momentary press

---

## Device Profiles

Device profiles simplify configuration by converting high-level actions into MIDI commands.

### Available Profiles

#### Neural DSP Quad Cortex
- Scene A/B/C/D selection
- Stomp and Row bypass
- Tuner control
- Preset navigation

#### Line 6 Helix
- Snapshot selection (1-8)
- Footswitch assignments
- Looper controls
- Tuner toggle

#### Line 6 HX Stomp
- Snapshot selection (1-3)
- Footswitch emulation
- Expression pedal control

#### Kemper Profiler
- Rig selection
- Effect bypass
- Tuner control
- Looper functions

#### Ableton Live (Template)
- Scene launch
- Track mute/solo
- Transport control
- Device control

#### Apple MainStage (Template)
- Patch changes
- Bypass controls
- Expression mapping

### Using Profiles

1. **Select Event**: Choose Press, Release, Long Press, or Long Release
2. **Change Source**: Select "Profile Action"
3. **Choose Device**: Pick target device profile
4. **Select Action**: Choose action from dropdown
5. **Preview MIDI**: View resolved commands
6. **Channel Override**: Optionally override MIDI channel

### Channel Overrides

Each profile action can override its default MIDI channel:
- Leave blank to use profile default
- Set specific channel (1-16) for custom routing

### Combining Profile and Custom Commands

You can mix profile and custom commands in the same event:
- Add profile action
- Click **+ Add Command** 
- Add custom CC, Note, or PC commands
- Commands execute in sequence

### Auto-Detection

When you select a button, the editor shows if existing MIDI commands match a known profile:
- **Badge indicator**: Shows matching profile
- **Tooltip**: Displays detected profile name
- Makes it easy to identify preconfigured buttons

---

## Conditional Actions

Conditional Actions enable buttons to execute different MIDI commands based on real-time conditions. This creates intelligent, context-aware behavior that adapts to your performance.

### What Are Conditional Actions?

A conditional action uses **IF/THEN/ELSE** logic:
- **IF** a condition is true (e.g., "Button 2 is ON")
- **THEN** execute these commands
- **ELSE** execute these other commands

This allows a single button to behave differently depending on the state of other buttons, received MIDI messages, expression pedal position, or encoder value.

### When to Use Conditionals

**Common Use Cases:**
- Send different CC values based on which scene is active
- Switch between two effect settings depending on channel selection
- Respond differently when host sends specific MIDI messages
- Adjust behavior based on expression pedal position
- Create "smart" buttons that adapt to performance context

### The 5 Condition Types

#### 1. Button State

Check if another button is currently ON or OFF.

**Fields:**
- **Button**: Which button to check (by index)
- **State**: "on" or "off"

**Example:**  
*"If Drive button (button 1) is ON, send CC50=127, else send CC50=0"*

**Use Case:** Delay effect that behaves differently based on whether distortion is active

#### 2. Button Keytime

Check which keytime state a multi-state button is currently in.

**Fields:**
- **Button**: Which button to check
- **Keytime**: State index (0 = first state, 1 = second state, etc.)

**Example:**  
*"If Scene button (button 0) is in keytime 2, send PC5, else send PC1"*

**Use Case:** Different boost settings for each scene

#### 3. Received MIDI

Check the value of a MIDI CC message received from the host.

**Fields:**
- **Channel**: MIDI channel (0-15)
- **CC Number**: Controller number to check
- **Operator**: Comparison type (==, !=, >, <, >=, <=)
- **Value**: Value to compare against (0-127)

**Example:**  
*"If received CC100 on channel 0 >= 64, send CC25=127, else send CC25=0"*

**Use Case:** Button behavior changes based on what the DAW sends (bidirectional sync)

#### 4. Expression Pedal

Check the current position of an expression pedal.

**Fields:**
- **Pedal**: "exp1" or "exp2"
- **Operator**: Comparison type (==, !=, >, <, >=, <=)
- **Value**: Value to compare against (0-127)

**Example:**  
*"If exp1 < 30, send PC0, else send PC1"*

**Use Case:** Auto-switch scenes based on pedal position (toe vs heel)

#### 5. Encoder Position

Check the current value of the rotary encoder.

**Fields:**
- **Operator**: Comparison type (==, !=, >, <, >=, <=)
- **Value**: Value to compare against (0-127)

**Example:**  
*"If encoder >= 64, send CC30=127, else send CC30=64"*

**Use Case:** Different effect intensity based on encoder position

### Creating Conditional Commands

#### Step 1: Add a Conditional Command

1. Select a button
2. Go to **Actions** section
3. Choose an event (Press, Release, Long Press, Long Release)
4. Click **+ Add Command**
5. Select **"Conditional"** from the Type dropdown

#### Step 2: Build the Condition

The Condition Builder appears with:
- **Condition Type** dropdown (Button State, Button Keytime, etc.)
- **Type-specific fields** (button index, CC number, operator, value)

1. Select condition type
2. Fill in the required fields
3. The condition is evaluated when the button is pressed

#### Step 3: Define THEN Commands

1. In the **"THEN"** section, click **+ Add Command**
2. Add MIDI commands that execute if condition is TRUE
3. Can add multiple commands (they execute in sequence)
4. Supports CC, Note, PC, PC Inc/Dec, and even nested conditionals

#### Step 4: Define ELSE Commands (Optional)

1. In the **"ELSE"** section, click **+ Add Command**
2. Add MIDI commands that execute if condition is FALSE
3. ELSE branch is optional (nothing happens if condition is false)

#### Step 5: Add Display Labels (Optional)

**THEN Label:**  
Text to show on display when THEN branch executes (max 6 chars)

**ELSE Label:**  
Text to show on display when ELSE branch executes (max 6 chars)

**Label Persist:**  
Checkbox - if enabled, conditional labels stay visible; if disabled, they timeout after 3 seconds

### Real-World Examples

#### Example 1: Scene-Aware Delay

**Goal:** Delay button sends different CC values based on active scene

**Setup:**
- Button 0 = "CLEAN" scene (toggle)
- Button 3 = "DELAY" with conditional

**Button 3 Configuration:**
```
Press:
  - Type: Conditional
    IF: Button State
      Button: 0
      State: on
    THEN:
      - CC 22, Value 64  (low delay for clean)
    ELSE:
      - CC 22, Value 127 (max delay for drive)
    THEN Label: "DLY LO"
    ELSE Label: "DLY HI"
```

**Result:** When CLEAN is active, delay is subtle; when drive is active, delay is maximum

#### Example 2: Expression-Based Auto-Switch

**Goal:** Button auto-switches scenes based on expression pedal position

**Setup:**
- Button 5 = "AUTO SCENE"

**Button 5 Configuration:**
```
Press:
  - Type: Conditional
    IF: Expression
      Pedal: exp1
      Operator: <
      Value: 40
    THEN:
      - PC 0  (scene 1 when heel down)
    ELSE:
      - PC 1  (scene 2 when toe up)
```

**Result:** Press button once, scene changes automatically based on pedal position

#### Example 3: Host-Responsive Button

**Goal:** Button behavior changes based on DAW state

**Setup:**
- DAW sends CC100=127 when recording, CC100=0 when stopped
- Button 8 = "SMART REC"

**Button 8 Configuration:**
```
Press:
  - Type: Conditional
    IF: Received MIDI
      Channel: 0
      CC: 100
      Operator: ==
      Value: 127
    THEN:
      - CC 50, Value 0    (stop recording)
    ELSE:
      - CC 50, Value 127  (start recording)
```

**Result:** Button toggles recording, adapting to current DAW state

#### Example 4: Multi-Scene Boost

**Goal:** Boost button sends different CC based on which scene button is active

**Setup:**
- Button 0 = Scene 1 (keytime 0)
- Button 0 = Scene 2 (keytime 1)
- Button 0 = Scene 3 (keytime 2)
- Button 6 = "BOOST" with conditionals

**Button 6 Configuration:**
```
Press:
  - Type: Conditional
    IF: Button Keytime
      Button: 0
      Keytime: 0
    THEN:
      - CC 70, Value 127  (clean boost)
    ELSE:
      - Type: Conditional
        IF: Button Keytime
          Button: 0
          Keytime: 1
        THEN:
          - CC 71, Value 127  (crunch boost)
        ELSE:
          - CC 72, Value 127  (lead boost)
```

**Result:** Boost button activates different boost CCs for each scene (nested conditionals)

### Advanced Features

#### Nested Conditionals

Conditionals can be nested inside THEN/ELSE branches for complex logic trees:
- IF button 1 is ON
  - THEN IF button 2 is ON
    - THEN send CC30=127
    - ELSE send CC30=64
  - ELSE send CC30=0

**Depth limit:** No hard limit, but 2-3 levels is typically sufficient

#### Mixing Conditionals with Regular Commands

You can mix conditional and regular MIDI commands in the same event:
```
Press:
  - CC 10, Value 127        (always send this)
  - Type: Conditional       (conditional command)
    IF: ...
    THEN: ...
  - PC 5                    (always send this after conditional)
```

Commands execute in the order they appear.

#### State Snapshot Evaluation

When using Button State or Button Keytime conditions:
- Condition is evaluated using button state **at press time**
- This ensures consistent behavior even if other buttons change during execution
- Prevents race conditions in complex setups

### UI Elements

**Condition Builder:**
- Dropdown for condition type selection
- Dynamic fields based on selected type
- Button label filtering (can't reference the button you're editing)

**Conditional Command Block:**
- Collapsible IF/THEN/ELSE structure
- Visual nesting for clarity
- Color-coded branches (green for THEN, red for ELSE)
- Drag handles for reordering (if applicable)

**Label Fields:**
- Then Label and Else Label text inputs
- 6 character limit
- Optional persistence checkbox

### Tips and Best Practices

**Start Simple:**
- Begin with basic IF/THEN logic before nesting
- Test each condition individually
- Use display labels to verify which branch executed

**Avoid Self-Reference:**
- Don't check the state of the button you're editing
- The UI prevents this, but it's conceptually important

**Use Labels for Debugging:**
- Set THEN/ELSE labels to see which branch executed
- Helpful during setup and troubleshooting

**Expression Threshold Values:**
- Expression pedals read 0-127
- Use < 30 for "heel down", > 100 for "toe up"
- Avoid exact equality (==) due to jitter

**Received MIDI Sync:**
- Ensure your host/DAW is sending the expected CC values
- Use MIDI Monitor to verify incoming messages
- Channel numbers are 0-indexed in conditions (0 = MIDI channel 1)

**Performance Considerations:**
- Conditionals are evaluated quickly (< 1ms)
- No noticeable latency even with nested conditionals
- Safe to use in live performance

### Troubleshooting

**Conditional Not Triggering:**
- Check condition fields are correct (button index, CC number, channel)
- Verify the condition is actually true (use MIDI Monitor)
- Ensure THEN/ELSE branches have commands added

**Wrong Branch Executing:**
- Double-check operator (>, <, ==, etc.)
- Verify value threshold is correct
- Use display labels to confirm which branch ran

**Button Index Confusion:**
- Button indices are 0-based: Button 1 = index 0, Button 2 = index 1
- The UI shows button labels for clarity
- Check Device Layout to confirm button numbers

**Display Label Not Showing:**
- Label must be 6 characters or less
- Check if conditional_label_persist is enabled in button config
- Non-select buttons timeout after 3 seconds unless persist is enabled

---

## Multi-State Buttons (Keytimes)

Keytimes allow buttons to cycle through multiple states, sending different MIDI commands each time pressed.

### Enabling Keytimes

1. Select a button
2. Find **Keytimes** field under Behavior
3. Set number of states (2-8)
4. State tabs appear below Actions

### State Configuration

Each state can override:
- **CC Number**: Different controller per state
- **CC On Value**: Different value when active
- **Color**: Different LED color per state
- **Label**: Different display name per state

### State Cycling

**Toggle/Select Mode:**
- First press → State 1 (sends Press commands)
- Second press → turns OFF (sends Release commands)
- Third press → State 2 (sends Press commands)
- Fourth press → turns OFF (sends Release commands)
- And so on...

**Example - Scene Cycling:**

Button labeled "SCENES" with 3 keytimes:
- **State 1**: CC 20, Red LED, "CLEAN"
- **State 2**: CC 21, Green LED, "CRUNCH"
- **State 3**: CC 22, Blue LED, "LEAD"

Each press cycles through clean → crunch → lead → off → clean...

### State Tabs

When keytimes > 1, tabs appear for each state:
- Click tab to edit that state's overrides
- Active state highlighted in color
- Leave fields empty to use base button settings

---

## Encoder Configuration

*Available on STD10 model only*

The rotary encoder provides continuous control and push-button functionality.

### Encoder Rotation

**Enable/Disable**  
Toggle encoder functionality on/off

**CC Number**  
MIDI controller to send (0-127)

**Label**  
Display name (max 8 characters)

**Range (Min/Max)**  
- Min: Starting value (0-127)
- Max: Ending value (0-127)
- Initial: Starting position on boot

**Steps**  
Number of discrete steps (leave blank for continuous)

**Channel**  
MIDI channel (1-16), uses global channel if blank

### Encoder Push Button

The encoder has a built-in push button with full button capabilities:

**Enable/Disable**  
Toggle push button functionality

**Mode**  
- Toggle
- Momentary

**CC Numbers**  
- CC On: Value sent when turned on (0-127)
- CC Off: Value sent when turned off (0-127)

**Display Settings**
- Label: Button name (max 8 characters)
- Channel: MIDI channel override (1-16)

---

## Expression Pedals

*Available on STD10 model only*

Configure up to two expression pedal inputs (EXP1 and EXP2).

### Expression Settings

**Enable/Disable**  
Toggle expression pedal input

**CC Number**  
MIDI controller to send (0-127)

**Label**  
Display name (max 8 characters)

**Range (Min/Max)**  
- Min: Value at heel position (0-127)
- Max: Value at toe position (0-127)

**Polarity**  
- Normal: Min at heel, Max at toe
- Inverted: Max at heel, Min at toe

**Threshold**  
Minimum movement to register change (reduces jitter)

**Channel**  
MIDI channel (1-16), uses global channel if blank

---

## Display Settings

Customize text sizes on the device screen.

### Text Size Options

**Button Text**  
Labels displayed for each button slot
- Small: Compact (~8px)
- Medium: Standard (20px)
- Large: Bold (60px)

**Status Text**  
Center status line (MIDI messages, system info)
- Small: Compact (~8px)
- Medium: Standard (20px)
- Large: Bold (60px)

**Expression Text**  
Expression pedal value display
- Small: Compact (~8px)
- Medium: Standard (20px)
- Large: Bold (60px)

**Note**: Very large text may overflow display for long labels. Use Medium for balanced appearance.

---

## MIDI Monitor

The **MIDI Monitor** is a professional debugging tool built into the config editor that displays real-time MIDI traffic between your device and other MIDI equipment.

### Opening the Monitor

1. Click the **MIDI Monitor** button in the toolbar (bottom toolbar)
2. The monitor panel opens at the bottom of the editor
3. Click again to close the panel

### Interface Overview

**Header Controls**
- **Port Selector**: Choose which MIDI port to monitor
- **Pause/Resume**: Pause message capture while keeping the monitor open
- **Clear**: Delete all captured messages
- **Export**: Save message log to a timestamped .txt file
- **Auto-scroll**: Toggle automatic scrolling to newest messages (enabled by default)

**Filter Bar**
- **Type**: Filter by message type (CC, Note On, Note Off, PC, SysEx, or All)
- **Channel**: Filter by MIDI channel 1-16 (or All channels)
- **Direction**: Filter by IN (incoming), OUT (outgoing), or All

**Message Display**
- Each message shows: timestamp, direction, channel, message type, and data
- **Color-coded type badges**: 
  - ● CC (Control Change)
  - ▲ Note On
  - ▼ Note Off
  - ■ PC (Program Change)
  - ◆ SysEx (System Exclusive)
  - ○ Other
- Messages are displayed newest-first (most recent at top)
- Badge shows filtered count / total count (e.g., "24 / 150")

### Common Use Cases

**1. Debugging Button Configuration**

When setting up a button, use the monitor to verify:
- **Correct CC numbers** are sent
- **Channel** matches your target device
- **Values** (0-127) are as expected
- **Multi-command sequences** execute in order

**Example workflow:**
1. Open MIDI Monitor
2. Press button on device
3. Verify message appears with correct parameters
4. If wrong, adjust button config and test again

**2. Learning MIDI from External Devices**

To map buttons to match an external device's MIDI output:
1. Select the **external device's MIDI output** in port selector
2. Set filter to **IN** (incoming) direction
3. Trigger the action on the external device (change preset, enable effect, etc.)
4. **Note the CC#, channel, and values** in the monitor
5. Configure your MIDI Captain button to send the same message

**Example:** To learn what MIDI your Helix sends for "Snapshot 3":
- Monitor: `12:34:56.789 IN Ch1 CC 69 = 2`
- Configure button: CC 69, Value 2, Channel 1

**3. Verifying Bidirectional Sync**

Test if your host software is sending MIDI back to the controller:
1. Set filter to **IN** direction
2. Change a parameter in your DAW/plugin host
3. If bidirectional MIDI is working, you'll see incoming CC/PC messages
4. Verify the CC# and channel match your button configuration

**4. Testing Multi-Command Actions**

When a button sends multiple MIDI commands:
1. Clear the log before testing
2. Press the button once
3. Count the number of messages (should match configured commands)
4. Verify order of execution

**5. Expression Pedal Calibration**

Check expression pedal MIDI output:
1. Filter by **CC** type and the pedal's assigned CC number
2. Move pedal through full range
3. Verify Min value at heel position
4. Verify Max value at toe position
5. Watch for jitter or unexpected jumps (increase threshold if needed)

### Message Format Examples

**Control Change:**
```
12:34:56.123 OUT Ch1 CC20 = 127
```
- Timestamp: 12:34:56 with 123ms precision
- Direction: OUT (sent by MIDI Captain)
- Channel: 1
- Type: Control Change #20
- Value: 127

**Note On:**
```
12:34:57.456 IN Ch10 Note 60 ON (vel 100)
```
- Direction: IN (received by MIDI Captain)
- Channel: 10 (drum channel)
- Note: 60 (Middle C)
- Velocity: 100

**Program Change:**
```
12:34:58.789 OUT Ch1 PC 5
```
- Program Change to program #5

**SysEx:**
```
12:34:59.012 IN SysEx [24 bytes]
```
- System Exclusive message (manufacturer-specific)
- Byte count shown in brackets

### Filtering Strategies

**Focus on Specific Button:**
1. Set **Type** filter to the message type used by the button (e.g., CC)
2. Filter by the button's **Channel**
3. Note the specific CC# in the message
4. Only messages matching both type and channel will appear

**Monitor MIDI Clock:**
- MIDI Clock is a specific type of message (not CC/Note/PC)
- Disable all filters to see clock messages
- Or filter **Type: Other** to exclude standard messages

**Capture Only Outgoing:**
- Set **Direction: OUT**
- Shows only messages sent by MIDI Captain
- Useful for verifying button presses work

**Watch Host Feedback:**
- Set **Direction: IN**
- Shows only messages received from host/DAW
- Useful for debugging bidirectional sync

### Export and Analysis

**Export Format:**

Clicking **Export** saves messages to a text file:
```
Filename: midi-log-1711238794123.txt

12:34:56.123 OUT Ch1 CC20 = 127
12:34:56.456 OUT Ch1 CC21 = 64
12:34:57.789 IN Ch1 CC20 = 127
```

**Use Cases:**
- Share logs when reporting issues
- Compare expected vs actual MIDI output
- Document MIDI implementation for complex setups
- Archive working configurations

### Performance Notes

**Buffer Size:**
- The monitor stores up to **1000 messages**
- Oldest messages are automatically removed when buffer is full
- For very high-throughput streams (MIDI clock), consider pausing periodically

**High-Throughput MIDI:**

The monitor uses an optimized ring buffer that can handle:
- MIDI Clock (24 messages per quarter note)
- Dense CC streams (rapid knob movements)
- Multiple simultaneous devices

**If experiencing lag:**
1. Use filters to reduce message count
2. Close other applications using MIDI
3. Pause monitoring when not actively debugging

### Tips

- **Leave monitor open during configuration** to see immediate feedback
- **Use Clear frequently** to focus on latest messages
- **Pause before inspecting** a specific message in detail
- **Export before closing** if you need to reference messages later
- **Filter aggressively** for complex MIDI setups with many devices
- **Check direction** — IN vs OUT helps isolate source of unexpected behavior

### Troubleshooting

**No Messages Appearing:**
1. Verify **port is selected** in dropdown
2. Check **device is connected** and powered
3. Ensure **MIDI cable** is connected (if using 5-pin DIN)
4. Try **pressing a configured button** to test OUT messages
5. Verify **USB MIDI** is working (check system MIDI settings)

**Messages from Wrong Device:**
1. Check **port selector** dropdown
2. Some MIDI interfaces create multiple virtual ports
3. Select the specific port for your device

**Filter Not Working:**
1. Messages are filtered client-side (all messages still captured)
2. Check **filter badge** shows filtered/total count
3. Try **Clear** and test again
4. Channel must be **exact match** (e.g., "1" ≠ "All")

**Export File Empty:**
1. Ensure **messages were captured** before export
2. Check **Downloads folder** for .txt file
3. Try **Clear, capture messages, then Export**

---

## Keyboard Shortcuts

### Global

- **⌘S** / **Ctrl+S**: Save configuration to device
- **⌘Z** / **Ctrl+Z**: Undo last change
- **⌘⇧Z** / **Ctrl+Shift+Z**: Redo change
- **⌘R** / **Ctrl+R**: Reload configuration from device
- **Esc**: Close modal dialogs

### Button Selection

- **↑** / **↓**: Select previous/next button
- **1-9, 0**: Quick select button by number

### Copy/Paste

- **⌘C** / **Ctrl+C**: Copy selected button (when focused)
- **⌘V** / **Ctrl+V**: Paste button configuration

---

## Tips and Best Practices

### Configuration Workflow

1. **Start with profiles** when possible - they handle complex MIDI correctly
2. **Use select groups** for mutually exclusive buttons (scenes, modes)
3. **Test one button at a time** before configuring entire board
4. **Save frequently** (⌘S) - changes are only written on save
5. **Use descriptive labels** - 6 characters is enough to identify function

### Button Modes

- **Toggle**: Best for on/off effects (delay, reverb, looper)
- **Momentary**: Best for hold-while-active (sustain, freeze, tap tempo)
- **Select**: Best for scenes, presets, or mode selection

#### One-Shot / Trigger Mode

To send MIDI **only on press** without any release message (like a drum pad or sample trigger), leave the **Release** event empty:

1. Add commands to **Press** event
2. Leave **Release** event completely empty
3. The button will trigger on press but be silent on release

This works with any button mode:
- **Momentary**: Trigger on press, silent on release
- **Toggle**: Sends MIDI only when turning ON, nothing when turning OFF

**Use cases:**
- Drum machines or samplers (trigger sounds)
- One-shot effects ("fire and forget" reverb/delay throws)
- Lighting cues or scene triggers
- Any device expecting only trigger messages (no "off" state)

#### Repeat Mode (Same Message Every Press)

To send the **same MIDI message every time** you press the button (instead of alternating ON/OFF), use **Toggle mode** with **identical commands** in both Press and Release events:

**Setup:**
1. Set button **Mode** to **Toggle**
2. Add commands to **Press** event (e.g., CC64=127)
3. Add **the exact same commands** to **Release** event (CC64=127)

**Result:**
- First press → button turns ON, sends Press commands
- Second press → button turns OFF, sends Release commands (identical to Press)
- Third press → button turns ON, sends Press commands again
- Etc.

The button alternates visual state (LED on/off) but sends the same MIDI message every time!

**Use cases:**
- **Tap tempo**: Send same CC repeatedly for BPM detection
- **Scene advance**: Increment scene number on each press
- **MIDI sync/nudge**: Repeated sync messages
- **Lighting cues**: Advance to next cue on each press
- Any device expecting the same trigger value repeatedly

**Visual feedback:** The LED will still toggle between ON and OFF states on each press, giving you visual confirmation that the button registered your press.

### MIDI Channels

- Use **global channel** unless you need multiple devices
- **Override channel** per button for multi-device setups
- Remember: Channel displayed as 1-16, stored as 0-15 internally

### Multi-Command Actions

- Order matters - commands execute in sequence
- Keep Press commands simple for instant response
- Use Release commands to cleanly disable effects
- Long Press for "alternate function" on same button

### Performance Tips

- **Disable dev mode** for live use (faster boot, no USB delay)
- **Use Off Mode: Dim** to see button layout in dark
- **Set default_selected** for startup scene/mode
- **Test select groups** thoroughly - wrong config can cause conflicts

### Expression Pedals

- **Calibrate range** using Min/Max to match your pedal's sweep
- **Increase threshold** if values jump erratically
- **Invert polarity** if pedal responds backward

---

## Troubleshooting

### Device Not Detected

**Problem**: Device doesn't appear in dropdown

**Solutions**:
1. **Enable USB drive mode**:
   - Power off device
   - Hold Switch 1 (top-left)
   - Power on while holding
   - Release after 2 seconds
2. **Enable dev mode** in existing config.json:
   - Add `"dev_mode": true` to config file
   - Device will always mount USB
3. **Check USB cable** - must be data cable, not charge-only
4. **Try different USB port** - some ports may have issues
5. **Restart editor** after connecting device

### Configuration Not Saving

**Problem**: Changes don't persist after save

**Solutions**:
1. Check **validation errors** in status bar
2. Ensure device is **not write-protected**
3. Verify **USB drive has space** (unlikely but possible)
4. Try **Reload** then save again
5. Check console for error messages

### Button Not Responding

**Problem**: Button presses don't send MIDI

**Solutions**:
1. Verify **MIDI commands** are configured for Press event
2. Check **MIDI channel** matches receiving device
3. Ensure **CC/Note numbers** are correct for target device
4. Test with **MIDI monitor** to verify messages are sent
5. Try **simple CC command** first to isolate issue

### Wrong LED Color or Behavior

**Problem**: LED doesn't match configuration

**Solutions**:
1. **Save configuration** first (changes don't apply until saved)
2. **Power cycle device** after saving
3. Check **Off Mode** - Dim vs Off affects appearance
4. Verify **color name** is in preset palette
5. Check for **state overrides** if using keytimes

### Encoder Not Working

**Problem**: Encoder doesn't send MIDI

**Solutions**:
1. Verify **encoder is enabled** in config
2. Check **CC number** doesn't conflict with buttons
3. Ensure **Min/Max range** is correct (Min < Max)
4. Test with **MIDI monitor** software
5. **STD10 only** - Mini6 has no encoder

### Expression Pedal Issues

**Problem**: Pedal sends wrong values or jumps

**Solutions**:
1. **Calibrate Min/Max** to match pedal's actual range
2. **Increase threshold** to reduce noise/jitter
3. Try **Inverted polarity** if range is backward
4. Verify **pedal is TRS** expression pedal (not TS)
5. Test **pedal with multimeter** to check resistance sweep

### Display Shows Wrong Text

**Problem**: Device screen doesn't match configuration

**Solutions**:
1. **Save and power cycle** device
2. Check **label max length** (6 chars for buttons, 8 for encoder)
3. Verify **text size settings** aren't too large
4. **ASCII characters only** - special chars may not render
5. Check for **firmware version** compatibility

### Keytimes Not Cycling

**Problem**: Multi-state button doesn't advance states

**Solutions**:
1. Verify **keytimes > 1** in configuration
2. Check **mode is Toggle or Select** (not Momentary)
3. Ensure **state overrides** are configured
4. **Save configuration** before testing
5. Watch **device screen** for state changes

### Unsaved Changes Warning

**Problem**: Editor warns about unsaved changes

**Solutions**:
1. **Intentional**: Click Save to write changes
2. **False positive**: Reload to discard unwanted changes
3. **Persistent warning**: Check if any field has validation error
4. **After reload**: Wait 2-3 seconds for device to reconnect

---

## Support and Resources

- **GitHub Issues**: [Report bugs or request features](https://github.com/MC-Music-Workshop/midi-captain-max/issues)
- **Documentation**: [Technical docs](https://github.com/MC-Music-Workshop/midi-captain-max/tree/main/docs)
- **Firmware Updates**: [Latest releases](https://github.com/MC-Music-Workshop/midi-captain-max/releases)

---

**Copyright © 2026 Maximilian Cascone. All rights reserved.**
