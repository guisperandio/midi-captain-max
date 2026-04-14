"""
Tests for ButtonPressHandler state machine.

Verifies button press/release state transitions and action dispatch.
"""

import sys
sys.path.insert(0, "firmware/circuitpython")

from handlers.button_press import ButtonPressHandler, ButtonPressState
from core.device_state import DeviceState
from core.button import ButtonState


class MockCallbacks:
    """Mock callback functions for testing."""
    
    def __init__(self):
        self.send_action_calls = []
        self.set_button_state_calls = []
        self.deselect_group_calls = []
        self.bank_switch_calls = []
        self.tap_tempo_calls = []
    
    def send_action(self, action_cfg, btn_num, idx, event_name):
        self.send_action_calls.append((action_cfg, btn_num, idx, event_name))
    
    def set_button_state(self, btn_num, on):
        self.set_button_state_calls.append((btn_num, on))
    
    def deselect_group(self, group_name, idx):
        self.deselect_group_calls.append((group_name, idx))
    
    def handle_bank_switch(self, target_idx):
        self.bank_switch_calls.append(target_idx)
    
    def record_tap_tempo(self, idx, now):
        self.tap_tempo_calls.append((idx, now))
    
    def has_long_press(self, config):
        return "long_press" in config or "long_release" in config
    
    def get_action_cfg(self, config, action_name, keytime):
        return config.get(action_name)
    
    def to_dict(self):
        """Convert to callbacks dict for ButtonPressHandler."""
        return {
            "send_action": self.send_action,
            "set_button_state": self.set_button_state,
            "deselect_group": self.deselect_group,
            "handle_bank_switch": self.handle_bank_switch,
            "record_tap_tempo": self.record_tap_tempo,
            "has_long_press": self.has_long_press,
            "get_action_cfg": self.get_action_cfg,
        }


def test_initial_state_is_idle():
    """Handler should start in IDLE state."""
    state = DeviceState(button_count=10)
    state.button_states = [ButtonState(cc=20, mode="toggle") for _ in range(10)]
    callbacks = MockCallbacks()
    
    handler = ButtonPressHandler(
        button_index=0,
        config={"mode": "toggle"},
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    assert handler.get_state() == ButtonPressState.IDLE


def test_press_transitions_to_pressed_state():
    """Pressing button should transition from IDLE to PRESSED."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    handler = ButtonPressHandler(
        button_index=0,
        config={"mode": "toggle"},
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Press button
    now = 1.0
    handler.on_press(now, btn_state)
    
    assert handler.get_state() == ButtonPressState.PRESSED
    assert state.press_start_times[0] == now


def test_double_press_detection():
    """Should detect double-press within timeout window."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    # Set up double-press config
    config = {
        "mode": "toggle",
        "double_press": [{"type": "cc", "cc": 30, "value": 127}],
        "double_press_timeout_ms": 300
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # First press/release
    state.last_release_times[0] = 1.0
    
    # Second press within timeout (250ms later)
    now = 1.25
    detected = handler.check_double_press(now)
    
    assert detected is True
    assert len(callbacks.send_action_calls) == 1
    assert callbacks.send_action_calls[0][3] == "double_press"
    assert state.double_press_consumed[0] is True


def test_double_press_timeout_exceeded():
    """Should NOT detect double-press outside timeout window."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    config = {
        "mode": "toggle",
        "double_press": [{"type": "cc", "cc": 30, "value": 127}],
        "double_press_timeout_ms": 300
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # First press/release
    state.last_release_times[0] = 1.0
    
    # Second press outside timeout (400ms later)
    now = 1.4
    detected = handler.check_double_press(now)
    
    assert detected is False
    assert len(callbacks.send_action_calls) == 0


def test_long_press_threshold():
    """Should transition to LONG_PRESS when threshold exceeded."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    config = {
        "mode": "toggle",
        "long_press": [{"type": "cc", "cc": 40, "value": 127}],
        "long_press_threshold_ms": 700
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Press button
    now = 1.0
    handler.on_press(now, btn_state)
    assert handler.get_state() == ButtonPressState.PRESSED
    
    # Check before threshold (600ms)
    handler.check_long_press(1.6, btn_state)
    assert handler.get_state() == ButtonPressState.PRESSED
    assert state.long_press_triggered[0] is False
    
    # Check after threshold (750ms)
    handler.check_long_press(1.75, btn_state)
    assert handler.get_state() == ButtonPressState.LONG_PRESS
    assert state.long_press_triggered[0] is True
    assert len(callbacks.send_action_calls) == 1
    assert callbacks.send_action_calls[0][3] == "long_press"


def test_release_after_short_press():
    """Short press should dispatch standard release actions."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="momentary")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    config = {
        "mode": "momentary",
        "press": [{"type": "cc", "cc": 20, "value": 127}],
        "release": [{"type": "cc", "cc": 20, "value": 0}]
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Press and release quickly
    handler.on_press(1.0, btn_state)
    handler.on_release(1.1, btn_state)
    
    # Should have dispatched release action
    release_calls = [c for c in callbacks.send_action_calls if c[3] == "release"]
    assert len(release_calls) == 1
    assert handler.get_state() == ButtonPressState.IDLE


def test_release_after_long_press():
    """Long press release should dispatch long_release action."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    config = {
        "mode": "toggle",
        "long_press": [{"type": "cc", "cc": 40, "value": 127}],
        "long_release": [{"type": "cc", "cc": 40, "value": 0}],
        "long_press_threshold_ms": 700
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Press, wait for long-press, then release
    handler.on_press(1.0, btn_state)
    handler.check_long_press(1.8, btn_state)  # Trigger long-press
    state.long_press_triggered[0] = True  # Mark as triggered
    handler.on_release(1.9, btn_state)
    
    # Should have dispatched long_release action
    long_release_calls = [c for c in callbacks.send_action_calls if c[3] == "long_release"]
    assert len(long_release_calls) == 1
    assert handler.get_state() == ButtonPressState.IDLE


def test_tap_mode_immediate_dispatch():
    """Tap mode should dispatch immediately with low latency."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="tap")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    state.blink_rate_ms = [500] * 10
    callbacks = MockCallbacks()
    
    config = {
        "mode": "tap",
        "press": [{"type": "cc", "cc": 20, "value": 127}]
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Press in tap mode
    now = 1.0
    handler.on_press(now, btn_state)
    
    # Should have dispatched immediately
    assert len(callbacks.send_action_calls) == 1
    assert callbacks.send_action_calls[0][3] == "press"
    
    # Should have recorded tap tempo
    assert len(callbacks.tap_tempo_calls) == 1
    assert state.blink_state[0] is True


def test_toggle_mode_flips_state():
    """Toggle mode should flip button state on press."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle", initial_state=False)
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    config = {
        "mode": "toggle",
        "press": [{"type": "cc", "cc": 20, "value": 127}],
        "release": [{"type": "cc", "cc": 20, "value": 0}]
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Initial state is OFF
    assert btn_state.state is False
    
    # Press button (no long-press config, so immediate)
    handler.on_press(1.0, btn_state)
    
    # State should flip to ON
    assert btn_state.state is True
    assert len(callbacks.set_button_state_calls) == 1
    assert callbacks.set_button_state_calls[0] == (1, True)


def test_select_group_deselects_others():
    """Pressing button with select_group should deselect others in group."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="select")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="select") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    config = {
        "mode": "select",
        "select_group": "scenes",
        "press": [{"type": "cc", "cc": 20, "value": 127}]
    }
    
    handler = ButtonPressHandler(
        button_index=0,
        config=config,
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Press button
    handler.on_press(1.0, btn_state)
    
    # Should have called deselect_group
    assert len(callbacks.deselect_group_calls) == 1
    assert callbacks.deselect_group_calls[0] == ("scenes", 0)


def test_bank_switch_button_detection():
    """Bank switch buttons should be detected and handled."""
    state = DeviceState(button_count=10)
    btn_state = ButtonState(cc=20, mode="toggle")
    state.button_states = [btn_state] + [ButtonState(cc=i+20, mode="toggle") for i in range(1, 10)]
    callbacks = MockCallbacks()
    
    # Define a mock bank manager
    class MockBankManager:
        def __init__(self):
            self.current_bank_index = 0
    
    bank_manager = MockBankManager()
    bank_switch_config = {"method": "button", "button_next": 1}
    banks = [{"name": "Bank 1"}, {"name": "Bank 2"}]
    
    handler = ButtonPressHandler(
        button_index=0,
        config={"mode": "toggle"},
        state=state,
        callbacks=callbacks.to_dict()
    )
    
    # Check if this is a bank switch button
    is_bank_button = handler.should_skip_for_bank_switch(bank_manager, bank_switch_config, banks)
    
    assert is_bank_button is True
    assert len(callbacks.bank_switch_calls) == 1
    assert callbacks.bank_switch_calls[0] == 1  # Target bank index
