"""
Tests for DeviceState class.

Verifies centralized state management and helper methods.
"""

import sys
sys.path.insert(0, "firmware/circuitpython")

from core.device_state import DeviceState, create_device_state


def test_device_state_initialization():
    """DeviceState should initialize with correct array sizes."""
    state = DeviceState(button_count=10)
    
    assert len(state.press_start_times) == 10
    assert len(state.button_states) == 0  # Empty until populated
    assert len(state.blink_state) == 10
    assert len(state.pc_values) == 16  # One per MIDI channel
    
    # Verify defaults
    assert state.encoder_value == 64
    assert state.encoder_push_state is False
    assert state.led_dirty is False
    assert state.is_showing_splash is True


def test_reset_button_press():
    """reset_button_press should clear press-related flags."""
    state = DeviceState(button_count=5)
    
    # Set some state
    state.press_start_times[2] = 1.5
    state.long_press_triggered[2] = True
    state.short_action_executed[2] = True
    state.state_at_press[2] = {"test": "data"}
    
    # Reset
    state.reset_button_press(2)
    
    # Verify cleared
    assert state.press_start_times[2] == 0.0
    assert state.long_press_triggered[2] is False
    assert state.short_action_executed[2] is False
    assert state.state_at_press[2] is None


def test_reset_double_press():
    """reset_double_press should clear double-press detection state."""
    state = DeviceState(button_count=5)
    
    # Set state
    state.last_release_times[3] = 2.5
    state.double_press_consumed[3] = True
    
    # Reset
    state.reset_double_press(3)
    
    # Verify cleared
    assert state.last_release_times[3] == 0.0
    assert state.double_press_consumed[3] is False


def test_led_dirty_flag():
    """LED dirty flag should track changes."""
    state = DeviceState(button_count=3)
    
    assert state.led_dirty is False
    
    state.mark_led_dirty()
    assert state.led_dirty is True
    
    state.clear_led_dirty()
    assert state.led_dirty is False


def test_received_cc_tracking():
    """Should track received CC values per channel/cc combination."""
    state = DeviceState(button_count=5)
    
    # Initially unset
    assert state.get_received_cc(0, 20) == 0
    
    # Set value
    state.set_received_cc(0, 20, 127)
    assert state.get_received_cc(0, 20) == 127
    
    # Different CC on same channel
    state.set_received_cc(0, 21, 64)
    assert state.get_received_cc(0, 21) == 64
    assert state.get_received_cc(0, 20) == 127  # Original unchanged
    
    # Different channel
    state.set_received_cc(1, 20, 32)
    assert state.get_received_cc(1, 20) == 32
    assert state.get_received_cc(0, 20) == 127  # Original channel unchanged


def test_pc_value_tracking():
    """Should track program change values per channel."""
    state = DeviceState(button_count=3)
    
    # Initial state
    assert state.pc_values[0] == 0
    assert state.pc_values[5] == 0
    
    # Update PC values
    state.update_pc_value(0, 10)
    assert state.pc_values[0] == 10
    
    state.update_pc_value(5, 127)
    assert state.pc_values[5] == 127
    assert state.pc_values[0] == 10  # Other channel unchanged
    
    # Out of range channel (should not crash)
    state.update_pc_value(20, 50)  # Channel 20 doesn't exist
    # Should be no-op, verify others unchanged
    assert state.pc_values[0] == 10


def test_create_device_state_factory():
    """Factory function should initialize with config values."""
    button_configs = [
        {"tap_rate_ms": 400},
        {"tap_rate_ms": 600},
        {},  # Missing tap_rate_ms - should use global default
    ]
    
    config = {"tap_rate_ms": 500}  # Global default
    
    state = create_device_state(
        button_count=3,
        button_configs=button_configs,
        config=config
    )
    
    # Check blink rates initialized from config
    assert state.blink_rate_ms[0] == 400  # Button-specific
    assert state.blink_rate_ms[1] == 600  # Button-specific
    assert state.blink_rate_ms[2] == 500  # Global default


def test_create_device_state_invalid_tap_rate():
    """Factory should handle invalid tap rate gracefully."""
    button_configs = [
        {"tap_rate_ms": -100},  # Invalid (negative)
        {"tap_rate_ms": "not a number"},  # Invalid (wrong type)
    ]
    
    config = {"tap_rate_ms": 500}
    
    state = create_device_state(
        button_count=2,
        button_configs=button_configs,
        config=config
    )
    
    # Should fall back to default for invalid values
    assert state.blink_rate_ms[0] == 500
    assert state.blink_rate_ms[1] == 500
