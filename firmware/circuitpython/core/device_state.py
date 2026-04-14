"""
Device state management for MIDI Captain firmware.

This module provides a centralized state container to replace scattered global
variables, improving testability and reducing coupling between handlers.

Author: Code refactoring - Phase 4
Date: 2026-04-14
"""

class DeviceState:
    """
    Centralized state container for device runtime state.
    
    Replaces 50+ global variables with organized state groups.
    Passed to handler functions instead of using global declarations.
    """
    
    def __init__(self, button_count):
        # type: (int) -> None
        """
        Initialize device state with default values.
        
        Args:
            button_count: Number of buttons on the device (10, 6, 4, 2, or 1)
        """
        self.button_count = button_count
        
        # Button state objects (from core.button.ButtonState)
        self.button_states = []  # type: list
        
        # Bank management
        self.bank_manager = None
        
        # Button press/release timing
        self.press_start_times = [0.0] * button_count
        self.last_release_times = [0.0] * button_count
        
        # Button action flags
        self.long_press_triggered = [False] * button_count
        self.short_action_executed = [False] * button_count
        self.double_press_consumed = [False] * button_count
        
        # State snapshots for select groups
        self.state_at_press = [None] * button_count
        
        # Visual feedback timers
        self.pc_flash_timers = [0.0] * button_count
        self.blink_state = [False] * button_count
        self.blink_next_toggle = [0.0] * button_count
        self.blink_rate_ms = [500] * button_count
        
        # Tap tempo tracking
        self.tap_timestamps = [[] for _ in range(button_count)]
        self.tap_active_until = [0.0] * button_count
        
        # MIDI state tracking for conditional actions
        self.received_cc_values = {}  # type: dict
        self.pc_values = [0] * 16  # Per-channel program change tracking
        
        # Encoder state (if present)
        self.encoder_value = 64  # Default center position
        self.encoder_push_state = False
        self.encoder_last_step_value = None
        
        # Expression pedal state (if present)
        self.exp1_min = 0
        self.exp1_max = 127
        self.exp1_last = -1
        self.exp2_min = 0
        self.exp2_max = 127
        self.exp2_last = -1
        
        # Display state
        self.label_timeout_return_to_select = 0.0
        self.last_activity_time = 0.0
        self.needs_wake_from_splash = False
        self.is_showing_splash = True
        
        # Performance monitoring
        self.led_dirty = False
        
    def reset_button_press(self, idx):
        # type: (int) -> None
        """
        Reset all press-related state for a button.
        
        Called when button is released or when transitioning states.
        
        Args:
            idx: Button index (0-based)
        """
        self.press_start_times[idx] = 0.0
        self.long_press_triggered[idx] = False
        self.short_action_executed[idx] = False
        self.state_at_press[idx] = None
    
    def reset_double_press(self, idx):
        # type: (int) -> None
        """
        Reset double-press detection state for a button.
        
        Called after a double-press is detected to prevent triple-press.
        
        Args:
            idx: Button index (0-based)
        """
        self.last_release_times[idx] = 0.0
        self.double_press_consumed[idx] = False
    
    def mark_led_dirty(self):
        # type: () -> None
        """Mark that LED state has changed and needs pixels.show()."""
        self.led_dirty = True
    
    def clear_led_dirty(self):
        # type: () -> None
        """Clear LED dirty flag after pixels.show() called."""
        self.led_dirty = False
    
    def get_received_cc(self, channel, cc_number):
        # type: (int, int) -> int
        """
        Get last received CC value for a channel/CC combination.
        
        Args:
            channel: MIDI channel (0-15)
            cc_number: CC number (0-127)
            
        Returns:
            Last received value (0-127), or 0 if never received
        """
        return self.received_cc_values.get(channel, {}).get(cc_number, 0)
    
    def set_received_cc(self, channel, cc_number, value):
        # type: (int, int, int) -> None
        """
        Record a received CC value for conditional action evaluation.
        
        Args:
            channel: MIDI channel (0-15)
            cc_number: CC number (0-127)
            value: CC value (0-127)
        """
        if channel not in self.received_cc_values:
            self.received_cc_values[channel] = {}
        self.received_cc_values[channel][cc_number] = value
    
    def update_pc_value(self, channel, program):
        # type: (int, int) -> None
        """
        Update program change tracking for a channel.
        
        Args:
            channel: MIDI channel (0-15)
            program: Program number (0-127)
        """
        if 0 <= channel < 16:
            self.pc_values[channel] = program


def create_device_state(button_count, button_configs, config):
    # type: (int, list, dict) -> DeviceState
    """
    Factory function to create and initialize a DeviceState instance.
    
    This helper initializes the state object with configuration-driven values
    like blink rates, thresholds, and button-specific settings.
    
    Args:
        button_count: Number of buttons on the device
        button_configs: List of button configuration dicts
        config: Global configuration dict
        
    Returns:
        Initialized DeviceState instance
    """
    state = DeviceState(button_count)
    
    # Initialize blink rates from config
    for i in range(button_count):
        try:
            btn_cfg = button_configs[i] if i < len(button_configs) else {}
            rate = btn_cfg.get("tap_rate_ms", config.get("tap_rate_ms", 500))
            if not isinstance(rate, int) or rate <= 0:
                rate = 500
            state.blink_rate_ms[i] = rate
        except Exception as e:
            print(f"[STATE] Blink rate config error for button {i}: {e}")
            state.blink_rate_ms[i] = 500
    
    return state
