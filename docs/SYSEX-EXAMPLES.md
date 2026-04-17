# SysEx Examples

This document provides SysEx (System Exclusive) message examples for various MIDI devices.

## What is SysEx?

SysEx messages are device-specific MIDI commands that allow control beyond standard CC/Note/PC messages. They always start with `F0` and end with `F7`.

## Format

```json
{
  "type": "sysex",
  "data": "F0 7F 7F 06 02 F7"
}
```

The `data` field should contain space-separated hex bytes.

---

## MIDI Machine Control (MMC)

Universal commands supported by many DAWs and hardware devices (MPC, sequencers, tape machines).

**Format**: `F0 7F [DeviceID] 06 [Command] F7`
- DeviceID: `7F` = all devices, `00-7F` = specific device

### Commands

| Command | Hex Data | Description |
|---------|----------|-------------|
| Stop | `F0 7F 7F 06 01 F7` | Stop playback |
| Play | `F0 7F 7F 06 02 F7` | Start playback |
| Deferred Play | `F0 7F 7F 06 03 F7` | Play from locate point |
| Fast Forward | `F0 7F 7F 06 04 F7` | Fast forward |
| Rewind | `F0 7F 7F 06 05 F7` | Rewind |
| Record Strobe | `F0 7F 7F 06 06 F7` | Punch in/out |
| Record Exit | `F0 7F 7F 06 07 F7` | Exit record |
| Record Pause | `F0 7F 7F 06 08 F7` | Pause recording |
| Pause | `F0 7F 7F 06 09 F7` | Pause playback |
| Eject | `F0 7F 7F 06 0A F7` | Eject |
| Reset | `F0 7F 7F 06 44 06 01 00 00 00 00 F7` | Reset to 00:00:00:00 |

### Example Config

```json
{
  "label": "PLAY",
  "color": "green",
  "mode": "momentary",
  "press": [{"type": "sysex", "data": "F0 7F 7F 06 02 F7"}],
  "release": [{"type": "sysex", "data": "F0 7F 7F 06 01 F7"}]
},
{
  "label": "REC",
  "color": "red",
  "mode": "toggle",
  "press": [{"type": "sysex", "data": "F0 7F 7F 06 06 F7"}],
  "long_press": [{"type": "sysex", "data": "F0 7F 7F 06 44 06 01 00 00 00 00 F7"}],
  "long_press_label": "RESET"
}
```

---

## Kemper Profiler

**Manufacturer ID**: `00 20 33` (Kemper)

### Common Commands

| Command | Hex Data | Description |
|---------|----------|-------------|
| Tap Tempo | `F0 00 20 33 02 7F 1D F7` | Tap tempo |
| Tuner On/Off | `F0 00 20 33 02 7F 7C F7` | Toggle tuner |
| Rig Up | `F0 00 20 33 02 7F 34 F7` | Next rig |
| Rig Down | `F0 00 20 33 02 7F 35 F7` | Previous rig |

### Example Config

```json
{
  "label": "TUNER",
  "color": "cyan",
  "mode": "momentary",
  "press": [{"type": "sysex", "data": "F0 00 20 33 02 7F 7C F7"}]
}
```

---

## Neural DSP Quad Cortex

**Manufacturer ID**: `00 01 78` (Neural DSP)

### Scene Selection

| Scene | Hex Data | Description |
|-------|----------|-------------|
| Scene A | `F0 00 01 78 43 00 F7` | Activate Scene A |
| Scene B | `F0 00 01 78 43 01 F7` | Activate Scene B |
| Scene C | `F0 00 01 78 43 02 F7` | Activate Scene C |
| Scene D | `F0 00 01 78 43 03 F7` | Activate Scene D |
| Scene E | `F0 00 01 78 43 04 F7` | Activate Scene E |
| Scene F | `F0 00 01 78 43 05 F7` | Activate Scene F |
| Scene G | `F0 00 01 78 43 06 F7` | Activate Scene G |
| Scene H | `F0 00 01 78 43 07 F7` | Activate Scene H |

### Example Config

```json
{
  "label": "QC A",
  "color": "blue",
  "mode": "toggle",
  "select_group": "qc_scene",
  "default_selected": true,
  "press": [{"type": "sysex", "data": "F0 00 01 78 43 00 F7"}]
},
{
  "label": "QC B",
  "color": "purple",
  "mode": "toggle",
  "select_group": "qc_scene",
  "press": [{"type": "sysex", "data": "F0 00 01 78 43 01 F7"}]
}
```

---

## Line 6 Helix

**Manufacturer ID**: `00 01 0C` (Line 6)

### Common Commands

| Command | Hex Data | Description |
|---------|----------|-------------|
| Snapshot 1 | `F0 00 01 0C 24 00 F7` | Activate Snapshot 1 |
| Snapshot 2 | `F0 00 01 0C 24 01 F7` | Activate Snapshot 2 |
| Snapshot 3 | `F0 00 01 0C 24 02 F7` | Activate Snapshot 3 |
| Snapshot 4 | `F0 00 01 0C 24 03 F7` | Activate Snapshot 4 |
| Tap Tempo | `F0 00 01 0C 24 10 F7` | Tap tempo |
| Tuner Toggle | `F0 00 01 0C 24 12 F7` | Toggle tuner |

### Example Config

```json
{
  "label": "SNAP1",
  "color": "green",
  "mode": "toggle",
  "select_group": "helix_snapshot",
  "press": [{"type": "sysex", "data": "F0 00 01 0C 24 00 F7"}]
}
```

---

## MIDI Time Code (MTC) Quarter Frame

For syncing to DAWs and sending time positions.

**Format**: `F0 7F [DeviceID] 01 01 [HH] [MM] [SS] [FF] F7`
- HH = hours, MM = minutes, SS = seconds, FF = frames

### Reset to 00:00:00:00

```json
{
  "type": "sysex",
  "data": "F0 7F 7F 01 01 00 00 00 00 F7"
}
```

---

## Multi-Command Actions

SysEx can be mixed with CC/Note/PC commands:

```json
{
  "label": "SCENE+",
  "press": [
    {"type": "cc", "cc": 20, "value": 127},
    {"type": "sysex", "data": "F0 7F 7F 06 02 F7"},
    {"type": "pc", "program": 5}
  ]
}
```

---

## Finding SysEx Commands

1. **Device Manual**: Check the MIDI implementation chart
2. **MIDI Monitor**: Use a MIDI monitoring tool to capture messages
3. **Community Forums**: Search for device-specific commands
4. **Trial and Error**: Test commands safely (won't damage hardware)

---

## Full Example Config

See [config-sysex-example.json](../firmware/circuitpython/config-sysex-example.json) for a complete configuration demonstrating:
- MMC transport controls (Play/Stop/Rec/Pause)
- Long-press for MMC Reset
- Kemper tuner toggle
- Quad Cortex scene switching
- Multi-command actions mixing SysEx + CC + PC

---

## Notes

- **SysEx messages ignore MIDI channels** — the channel selector in the UI is disabled for SysEx commands
- **Validation**: Firmware validates format (must start with F0, end with F7)
- **Manufacturer IDs**: Standard (1 byte) or Extended (3 bytes starting with 00)
- **Performance**: Multi-command actions apply a 2ms inter-command delay between all commands (including SysEx) for MIDI buffer management; SysEx has no additional delay
- **Bidirectional**: Firmware currently sends SysEx but does not process incoming SysEx (planned for future release)

---

## Resources

- [MIDI Manufacturers Association - SysEx](https://www.midi.org/)
- [MMC Specification](http://midi.teragonaudio.com/tech/midispec/mmc.htm)
- Device-specific MIDI implementation guides (check manufacturer websites)
