# MIDI Captain MAX Firmware

Custom CircuitPython firmware for Paint Audio MIDI Captain foot controllers.

## Project Structure

```
firmware/circuitpython/
├── code.py                 # Main entry point
├── boot.py                 # Boot configuration
├── config.json             # Default device configuration
├── VERSION                 # Firmware version (generated)
│
├── core/                   # Core modules (no hardware deps except config)
│   ├── button.py          # Button state management
│   ├── banks.py           # Bank/page management
│   ├── colors.py          # Color palette and utilities
│   ├── config.py          # Configuration loading and validation
│   ├── constants.py       # Global constants and defaults
│   ├── condition_evaluator.py  # Conditional action evaluation
│   └── message_pool.py    # Shared MIDI message objects
│
├── handlers/               # Hardware interaction handlers
│   ├── button.py          # Button press/release handling
│   ├── display.py         # Display and label updates
│   ├── encoder.py         # Encoder and expression pedal handling
│   ├── midi.py            # MIDI I/O operations
│   └── timers.py          # Timer and blink management
│
├── utils/                  # Pure utility functions (NO dependencies)
│   ├── timing.py          # Performance monitoring tools
│   └── __init__.py        # Package exports
│
├── devices/                # Hardware-specific constants
│   ├── std10.py           # STD10 (10-switch) configuration
│   └── mini6.py           # Mini6 (6-switch) configuration
│
├── fonts/                  # PCF display fonts
│   ├── PTSans-Regular-20.pcf
│   └── PTSans-Bold-60.pcf
│
└── lib/                    # CircuitPython libraries (.mpy format)
    └── adafruit_*.mpy
```

## Import Hierarchy

To prevent circular import issues, follow this strict import hierarchy:

```
1. utils/      ← Pure functions, no dependencies
   ↓
2. core/       ← Business logic, minimal hardware deps
   ↓
3. handlers/   ← Hardware interaction, imports from core
   ↓
4. code.py     ← Main orchestration, imports from all above
```

### Rules

**✅ ALLOWED:**
- `utils/` can import from standard library only
- `core/` can import from `utils/` and standard library
- `handlers/` can import from `core/` and `utils/`
- `code.py` can import from anywhere

**❌ FORBIDDEN:**
- `utils/` importing from `core/` or `handlers/`
- `core/` importing from `handlers/`
- `handlers/` importing from `code.py`
- Any circular imports between modules

### Guidelines

1. **Keep `utils/` dependency-free** - No board, digitalio, neopixel, etc.
   - Move pure functions here (e.g., math, string manipulation, timing)
   - Example: `clamp_value(val, min, max)` → utils

2. **Keep `core/` hardware-minimal** - Config, constants, business logic only
   - No direct hardware access (no `pixels`, `switches`, `display`)
   - Hardware-agnostic state management (ButtonState, BankManager)
   - Example: Button state logic → core, LED updates → handlers

3. **Use `handlers/` for hardware** - All board, GPIO, MIDI, display operations
   - Import business logic from `core/`
   - Call hardware APIs (neopixel, displayio, usb_midi)
   - Example: `set_button_state()` calls `pixels.show()`

4. **`code.py` orchestrates** - Wire everything together, main loop, global state
   - Import handlers and call them
   - Manage global hardware objects (pixels, switches, midi_usb)
   - Keep `code.py` thin - delegate to handlers

## Adding New Code

### Where should my code go?

**Pure utility (no dependencies)?** → `utils/`
```python
# utils/math_helpers.py
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))
```

**Business logic (config, validation, state)?** → `core/`
```python
# core/validation.py
def validate_cc_number(cc):
    if not 0 <= cc <= 127:
        raise ValueError(f"CC {cc} out of range")
```

**Hardware interaction?** → `handlers/`
```python
# handlers/led.py
def set_led_color(index, color, pixels):
    pixels[index] = color
    pixels.show()
```

**Main loop orchestration?** → `code.py`
```python
# code.py
while True:
    handle_switches()
    handle_midi()
    handle_encoder()
```

## Testing

CircuitPython code is tested on desktop Python using mocks:

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_*.py    # Run specific test file
```

Mocks are in `tests/mocks/` for hardware modules (board, neopixel, etc.).

## Development Workflow

1. **Make changes** - Edit code in `firmware/circuitpython/`
2. **Run tests** - `pytest` to verify functionality
3. **Deploy to device** - `./tools/deploy.sh` (auto-detects mount point)
4. **Test on hardware** - Observe serial output with `screen`

See [docs/screen-cheatsheet.md](../../docs/screen-cheatsheet.md) for serial monitoring.

## Performance Monitoring

Enable optional performance monitoring in `code.py`:

```python
from utils.timing import PerformanceMonitor

ENABLE_PERFORMANCE_MONITORING = True  # Set False for production

# In main loop:
if ENABLE_PERFORMANCE_MONITORING:
    with PerformanceMonitor("MIDI processing", threshold_ms=5):
        handle_midi()
```

Monitors operation timing and warns if threshold exceeded.

## Version Management

- `VERSION` file is auto-generated from git tags during build/deploy
- Never manually edit `VERSION` - it's written by CI and deploy scripts
- Format: `v{major}.{minor}.{patch}[-{prerelease}.{n}]` (e.g., `v1.0.0-alpha.1`)
- Falls back to `"dev"` if git tags unavailable

## Configuration

Device behavior is controlled by `config.json`:

- **Button mappings** - MIDI CC/PC/Note assignments per button
- **Display settings** - Text sizes for button labels, status, expression
- **USB drive name** - Custom volume label (FAT32 11-char limit)
- **Dev mode** - Always mount USB drive (bypass Switch 1 hold)
- **Banks** - Multiple button configurations switchable via MIDI/button

See config editor app (`config-editor/`) for graphical configuration.

## CircuitPython Constraints

This firmware targets **CircuitPython 7.x** (tested on 7.3.1):

- **No asyncio** - Use polling loops instead
- **Limited syntax** - No walrus operator, match/case, dict unpacking in literals
- **Missing str methods** - No `isalnum()`, `isalpha()`, `isdigit()` (use manual checks)
- **Memory constrained** - Object pooling for frequently-created objects
- **No autoreload** - Disabled in `boot.py` for performance stability

CI enforces compatibility with syntax guards (see `.github/workflows/ci.yml`).

## License

Copyright (c) 2026 Maximilian Cascone - All rights reserved.

See [LICENSE](../../LICENSE) for full terms.
