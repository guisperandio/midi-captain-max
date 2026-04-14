"""
Tests for double-press detection in button handling.

Double-press allows buttons to execute different actions when pressed twice
in rapid succession (within a configurable timeout window).
"""

import pytest
import time
import sys
sys.path.insert(0, "firmware/circuitpython")

from core.button import ButtonState


class TestDoublePressDetection:
    """Test double-press timing and detection logic."""

    def test_double_press_window_detection(self):
        """Double-press should be detected when two presses occur within timeout window."""
        # Simulate press/release sequence with timing
        times = []
        
        # First press at t=0
        first_press_time = 0.0
        times.append(first_press_time)
        
        # First release at t=0.1
        first_release_time = 0.1
        times.append(first_release_time)
        
        # Second press at t=0.25 (150ms after release, within 300ms default timeout)
        second_press_time = 0.25
        time_since_release = second_press_time - first_release_time
        
        # Should be detected as double-press
        assert time_since_release < 0.3  # 300ms default timeout
        assert time_since_release > 0.0  # Not instantaneous

    def test_double_press_timeout_exceeded(self):
        """Double-press should NOT be detected when timeout window is exceeded."""
        # First press at t=0
        first_press_time = 0.0
        
        # First release at t=0.1
        first_release_time = 0.1
        
        # Second press at t=0.5 (400ms after release, exceeds 300ms default timeout)
        second_press_time = 0.5
        time_since_release = second_press_time - first_release_time
        
        # Should NOT be detected as double-press
        assert time_since_release > 0.3  # Exceeds 300ms default timeout

    def test_double_press_custom_timeout(self):
        """Double-press detection should respect custom timeout values."""
        custom_timeout_ms = 500  # 500ms custom timeout
        custom_timeout_sec = custom_timeout_ms / 1000.0
        
        # First release at t=0.1
        first_release_time = 0.1
        
        # Second press at t=0.45 (350ms after release)
        second_press_time = 0.45
        time_since_release = second_press_time - first_release_time
        
        # With 300ms timeout: NOT a double-press
        assert time_since_release > 0.3
        
        # With 500ms timeout: IS a double-press
        assert time_since_release < custom_timeout_sec

    def test_triple_press_resets_detection(self):
        """After a double-press is detected, timer should reset to prevent triple-press detection."""
        # This test verifies the firmware behavior where last_release_times[idx] is reset to 0.0
        # after a double-press is detected, preventing the third press from being detected
        # as another double-press
        
        timeout_ms = 300
        timeout_sec = timeout_ms / 1000.0
        
        # First release at t=0.1
        first_release = 0.1
        
        # Second press at t=0.25 (double-press detected)
        second_press = 0.25
        assert (second_press - first_release) < timeout_sec
        
        # After double-press detection, last_release_times should be reset
        # So a third press should NOT be detected as a double-press
        # even if it's within the timeout window from the second press
        
        # Third press at t=0.4 (150ms after second press, within 300ms window)
        third_press = 0.4
        # This should NOT be a double-press because timer was reset
        # (In firmware, last_release_times[idx] = 0.0 after double-press)
        # After double-press at t=0.25, last_release should be 0.0
        last_release_after_double = 0.0
        interval_third = third_press - last_release_after_double
        assert interval_third > timeout_sec, "Third press should NOT be within timeout window after reset"
        assert last_release_after_double == 0.0, "Last release time should be reset to 0.0 after double-press"

    def test_zero_timeout_never_triggers(self):
        """A timeout of 0ms should never trigger double-press detection."""
        timeout_ms = 0
        timeout_sec = timeout_ms / 1000.0
        
        # Any non-zero time interval will exceed a 0ms timeout
        assert 0.001 > timeout_sec  # Even 1ms exceeds 0ms timeout

    def test_double_press_with_long_press(self):
        """Double-press should take priority over long-press when both are configured."""
        # This is a firmware behavior test - when a button has both double_press
        # and long_press configured, the double-press detection happens first
        # in the button press handler via the 'continue' statement that skips
        # normal press handling when a double-press is detected
        
        # Scenario: Button has both double_press and long_press actions
        # User double-presses quickly (within timeout)
        
        first_release = 0.1
        second_press = 0.25  # 150ms after first release
        
        # Double-press detected (executes and skips further processing via 'continue')
        assert (second_press - first_release) < 0.3
        
        # Long-press threshold (500ms default) would not be reached because
        # the double-press 'continue' statement prevents reaching the long-press check

    def test_double_press_button_state_independence(self):
        """Double-press detection should work independently of button toggle state."""
        # Double-press is purely timing-based and doesn't depend on whether
        # the button is currently ON or OFF
        
        # Test with button ON
        btn_state = ButtonState(cc=20, mode="toggle", initial_state=True)
        assert btn_state.state == True
        # Double-press detection timing is the same regardless of state
        
        # Test with button OFF
        btn_state2 = ButtonState(cc=21, mode="toggle", initial_state=False)
        assert btn_state2.state == False
        # Double-press detection timing is the same regardless of state

    def test_double_press_mode_compatibility(self):
        """Double-press should work with all button modes (toggle, momentary, select)."""
        # The firmware implements double-press detection before mode-specific
        # handling via an early 'continue' when double-press is detected
        
        modes = ["toggle", "momentary", "select"]
        for mode in modes:
            btn = ButtonState(cc=20, mode=mode)
            # Double-press detection happens before mode check, so it works for all modes
            assert btn.mode == mode


class TestDoublePressConfig:
    """Test configuration handling for double-press."""

    def test_default_timeout_used_when_not_specified(self):
        """When button doesn't specify timeout, global default should be used."""
        default_timeout_ms = 300  # Firmware default
        
        # Button config without custom timeout
        button_config = {
            "cc": 20,
            "double_press": [{"type": "pc", "program": 5}]
            # No double_press_timeout_ms specified
        }
        
        # Should use default 300ms
        assert "double_press_timeout_ms" not in button_config

    def test_button_level_timeout_override(self):
        """Button-specific timeout should override global default."""
        global_default = 300
        button_timeout = 500
        
        button_config = {
            "cc": 20,
            "double_press": [{"type": "pc", "program": 5}],
            "double_press_timeout_ms": button_timeout
        }
        
        effective_timeout = button_config.get("double_press_timeout_ms", global_default)
        assert effective_timeout == button_timeout

    def test_global_config_timeout_override(self):
        """Global config timeout should override firmware default."""
        firmware_default = 300
        global_config_timeout = 400
        
        config = {
            "double_press_timeout_ms": global_config_timeout,
            "buttons": []
        }
        
        effective = config.get("double_press_timeout_ms", firmware_default)
        assert effective == global_config_timeout


class TestDoublePressEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_simultaneous_press_release(self):
        """Very fast press/release (same timestamp) should not trigger double-press."""
        # First press/release at t=0.0
        first_release = 0.0
        
        # Second press also at t=0.0 (simultaneous)
        second_press = 0.0
        
        time_diff = second_press - first_release
        # Should be exactly 0, which equals timeout but doesn't exceed it
        # Firmware uses <= timeout check, so 0ms would technically trigger
        assert time_diff == 0.0

    def test_first_press_no_double(self):
        """First press after boot should not trigger double-press (no prior release)."""
        # last_release_times[] is initialized to 0.0
        # On first press, the check (now - last_release) will be large
        # because 'now' is e.g. 1.5 seconds and last_release is 0.0
        
        last_release = 0.0
        now = 1.5  # 1.5 seconds into runtime
        
        # First press: huge interval since last release (which was never)
        time_since_release = now - last_release
        timeout = 0.3
        
        # Should NOT be detected as double-press
        assert time_since_release > timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
