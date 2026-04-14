"""
Button press handler with state machine.

Extracts button press/release logic from the monolithic handle_switches()
function into a testable, composable state machine.

Author: Phase 4 refactoring
Date: 2026-04-14
"""

import time


class ButtonPressState:
    """Enum-like constants for button press states."""
    IDLE = "idle"
    PRESSED = "pressed"
    LONG_PRESS = "long_press"
    RELEASED = "released"


class ButtonPressHandler:
    """
    State machine for button press/release lifecycle.
    
    Manages transitions through:
    IDLE → PRESSED → (LONG_PRESS) → RELEASED → IDLE
    
    Encapsulates logic for:
    - Double-press detection
    - Long-press threshold monitoring
    - Short press vs long press dispatch
    - Mode-specific behavior (toggle, momentary, select, tap)
    """
    
    def __init__(self, button_index, config, state, callbacks):
        # type: (int, dict, object, dict) -> None
        """
        Initialize button press handler.
        
        Args:
            button_index: Button index (0-based)
            config: Button configuration dict
            state: DeviceState instance
            callbacks: Dict of callback functions:
                - send_action: (action_cfg, btn_num, idx, event_name) -> None
                - set_button_state: (btn_num, on) -> None
                - deselect_group: (group_name, idx) -> None
                - handle_bank_switch: (target_idx) -> None
                - record_tap_tempo: (idx, now) -> None
                - has_long_press: (btn_config) -> bool
                - get_action_cfg: (btn_config, action_name, keytime) -> list
        """
        self.idx = button_index
        self.btn_num = button_index + 1  # 1-indexed button number
        self.config = config
        self.state = state
        self.callbacks = callbacks
        
        # Current state in the state machine
        self.current_state = ButtonPressState.IDLE
        
        # Config shortcuts
        self.mode = config.get("mode", "toggle")
        self.long_enabled = callbacks["has_long_press"](config)
        
    def get_state(self):
        # type: () -> str
        """Get current state machine state."""
        return self.current_state
    
    def should_skip_for_bank_switch(self, bank_manager, bank_switch_config, banks):
        # type: (object, dict, list) -> bool
        """
        Check if this button is a bank switch button.
        
        Returns:
            True if button press was consumed by bank switching
        """
        if not bank_manager or not bank_switch_config or len(banks) == 0:
            return False
        
        method = bank_switch_config.get("method", "button")
        if method != "button":
            return False
        
        # Legacy single button cycling
        bank_btn = bank_switch_config.get("button")
        # New dual button mode
        bank_next = bank_switch_config.get("button_next")
        bank_prev = bank_switch_config.get("button_prev")
        
        if bank_next and self.btn_num == bank_next:
            target_idx = (bank_manager.current_bank_index + 1) % len(banks)
            self.callbacks["handle_bank_switch"](target_idx)
            return True
        elif bank_prev and self.btn_num == bank_prev:
            target_idx = (bank_manager.current_bank_index - 1) % len(banks)
            self.callbacks["handle_bank_switch"](target_idx)
            return True
        elif bank_btn and self.btn_num == bank_btn and not bank_next and not bank_prev:
            target_idx = (bank_manager.current_bank_index + 1) % len(banks)
            self.callbacks["handle_bank_switch"](target_idx)
            return True
        
        return False
    
    def check_double_press(self, now):
        # type: (float) -> bool
        """
        Check if this press qualifies as a double-press.
        
        Args:
            now: Current monotonic time
            
        Returns:
            True if double-press was detected and handled
        """
        double_press_cfg = self.config.get("double_press")
        if not double_press_cfg:
            return False
        
        timeout_ms = self.config.get("double_press_timeout_ms", 300)
        timeout_sec = timeout_ms / 1000.0
        last_release = self.state.last_release_times[self.idx]
        
        if last_release > 0 and (now - last_release) <= timeout_sec:
            # Double-press detected!
            print(f"[DOUBLE-PRESS] Button {self.btn_num} double-pressed (interval: {(now - last_release)*1000:.0f}ms)")
            self.callbacks["send_action"](double_press_cfg, self.btn_num, self.idx, "double_press")
            self.state.short_action_executed[self.idx] = True
            self.state.double_press_consumed[self.idx] = True
            self.state.last_release_times[self.idx] = 0.0
            return True
        
        return False
    
    def handle_tap_mode_press(self, now, btn_state):
        # type: (float, object) -> None
        """
        Handle tap tempo mode press (critical path - low latency).
        
        Args:
            now: Current monotonic time
            btn_state: ButtonState object
        """
        # CRITICAL PATH: Send MIDI first for minimal latency
        btn_state.advance_keytime()
        press_cfg = self.callbacks["get_action_cfg"](self.config, "press", btn_state.get_keytime())
        if press_cfg:
            self.callbacks["send_action"](press_cfg, self.btn_num, self.idx, "press")
            self.state.short_action_executed[self.idx] = True
        
        # Bookkeeping after MIDI
        self.callbacks["record_tap_tempo"](self.idx, now)
        self.state.blink_state[self.idx] = True
        if self.state.blink_rate_ms[self.idx] > 0:
            beat_interval = self.state.blink_rate_ms[self.idx] / 1000.0
            flash_duration = max(0.05, min(0.2, beat_interval * 0.2))
            self.state.blink_next_toggle[self.idx] = now + flash_duration
        else:
            self.state.blink_next_toggle[self.idx] = now + 0.1
    
    def on_press(self, now, btn_state):
        # type: (float, object) -> bool
        """
        Handle button press event.
        
        Args:
            now: Current monotonic time
            btn_state: ButtonState object
            
        Returns:
            True if press was handled (skip further processing)
        """
        if self.current_state != ButtonPressState.IDLE:
            return False  # Ignore if not idle
        
        # Initialize press timing
        if not self.state.press_start_times[self.idx]:
            self.state.press_start_times[self.idx] = now
            self.state.long_press_triggered[self.idx] = False
            self.state.short_action_executed[self.idx] = False
            # Capture snapshot for select groups
            self.state.state_at_press[self.idx] = {
                'states': [self.state.button_states[si].state for si in range(len(self.state.button_states))],
                'keytimes': [self.state.button_states[si].current_keytime for si in range(len(self.state.button_states))],
            }
        
        # Transition to PRESSED state
        self.current_state = ButtonPressState.PRESSED
        
        # Handle tap mode immediately (critical path)
        if self.mode == "tap":
            self.handle_tap_mode_press(now, btn_state)
        
        # Dispatch immediate actions for modes without long-press
        if not self.long_enabled and self.mode != "tap":
            self._dispatch_immediate_press(btn_state)
        elif self.mode == "momentary":
            # Momentary with long-press: dispatch press immediately
            btn_state.advance_keytime()
            press_cfg = self.callbacks["get_action_cfg"](self.config, "press", btn_state.get_keytime())
            if press_cfg:
                self.callbacks["send_action"](press_cfg, self.btn_num, self.idx, "press")
            self.callbacks["set_button_state"](self.btn_num, True)
        
        return False
    
    def _dispatch_immediate_press(self, btn_state):
        # type: (object) -> None
        """Dispatch press action for modes without long-press delay."""
        if self.mode in ("toggle", "normal", "select"):
            btn_state.advance_keytime()
            new_state = self._calculate_new_state(btn_state)
            btn_state.state = new_state
            self.callbacks["set_button_state"](self.btn_num, new_state)
            
            if new_state:
                sg = self.config.get("select_group")
                if sg:
                    self.callbacks["deselect_group"](sg, self.idx)
            
            action_name = "press" if new_state else "release"
            action_cfg = self.callbacks["get_action_cfg"](self.config, action_name, btn_state.get_keytime())
            if action_cfg:
                self.callbacks["send_action"](action_cfg, self.btn_num, self.idx, action_name)
                self.state.short_action_executed[self.idx] = True
        else:
            # Momentary or other modes
            press_cfg = self.callbacks["get_action_cfg"](self.config, "press", btn_state.get_keytime())
            if press_cfg:
                self.callbacks["send_action"](press_cfg, self.btn_num, self.idx, "press")
                self.state.short_action_executed[self.idx] = True
            
            if self.mode == "momentary":
                self.callbacks["set_button_state"](self.btn_num, True)
    
    def _calculate_new_state(self, btn_state):
        # type: (object) -> bool
        """Calculate new button state for toggle/select modes."""
        if btn_state.keytimes > 1:
            return True
        elif self.mode == "select":
            return True
        elif self.config.get("select_group") and btn_state.state:
            return True  # Radio button: stay selected
        elif self.mode in ("toggle", "normal"):
            return not btn_state.state
        else:
            return True
    
    def check_long_press(self, now, btn_state):
        # type: (float, object) -> None
        """
        Check if long-press threshold has been exceeded.
        
        Called from main loop for buttons in PRESSED state.
        
        Args:
            now: Current monotonic time
            btn_state: ButtonState object
        """
        if self.current_state != ButtonPressState.PRESSED:
            return
        
        if not self.long_enabled:
            return
        
        if self.state.long_press_triggered[self.idx]:
            return  # Already triggered
        
        press_start = self.state.press_start_times[self.idx]
        if press_start == 0:
            return
        
        # Get threshold (button-level or global)
        threshold_ms = self.config.get("long_press_threshold_ms", 700)
        threshold_sec = threshold_ms / 1000.0
        
        if (now - press_start) >= threshold_sec:
            # Long-press threshold exceeded!
            self.current_state = ButtonPressState.LONG_PRESS
            self.state.long_press_triggered[self.idx] = True
            
            # Dispatch long_press action
            long_press_cfg = self.callbacks["get_action_cfg"](self.config, "long_press", btn_state.get_keytime())
            if long_press_cfg:
                self.callbacks["send_action"](long_press_cfg, self.btn_num, self.idx, "long_press")
    
    def on_release(self, now, btn_state):
        # type: (float, object) -> None
        """
        Handle button release event.
        
        Args:
            now: Current monotonic time
            btn_state: ButtonState object
        """
        if self.current_state == ButtonPressState.IDLE:
            return
        
        # Reset timing
        self.state.press_start_times[self.idx] = 0.0
        was_long = self.state.long_press_triggered[self.idx]
        self.state.long_press_triggered[self.idx] = False
        
        # Record release time for double-press detection
        if self.state.double_press_consumed[self.idx]:
            self.state.double_press_consumed[self.idx] = False
        else:
            self.state.last_release_times[self.idx] = now
        
        # Dispatch appropriate release action
        if was_long:
            self._handle_long_release(btn_state)
        else:
            self._handle_short_release(btn_state)
        
        # Transition back to IDLE
        self.current_state = ButtonPressState.IDLE
    
    def _handle_long_release(self, btn_state):
        # type: (object) -> None
        """Handle release after long-press."""
        long_release_cfg = self.callbacks["get_action_cfg"](self.config, "long_release", btn_state.get_keytime())
        if long_release_cfg:
            self.callbacks["send_action"](long_release_cfg, self.btn_num, self.idx, "long_release")
        
        # Restore LED state
        if self.mode == "momentary":
            self.callbacks["set_button_state"](self.btn_num, False)
        else:
            self.callbacks["set_button_state"](self.btn_num, btn_state.state)
    
    def _handle_short_release(self, btn_state):
        # type: (object) -> None
        """Handle release after short press."""
        if self.long_enabled and self.mode in ("toggle", "normal", "select", "tap"):
            if not self.state.short_action_executed[self.idx]:
                # Deferred action - execute now
                btn_state.advance_keytime()
                new_state = self._calculate_new_state(btn_state)
                btn_state.state = new_state
                self.callbacks["set_button_state"](self.btn_num, new_state)
                
                if new_state:
                    sg = self.config.get("select_group")
                    if sg:
                        self.callbacks["deselect_group"](sg, self.idx)
                
                action_name = "press" if new_state else "release"
                action_cfg = self.callbacks["get_action_cfg"](self.config, action_name, btn_state.get_keytime())
                if action_cfg:
                    self.callbacks["send_action"](action_cfg, self.btn_num, self.idx, action_name)
        elif self.mode == "momentary":
            # Momentary mode release
            release_cfg = self.callbacks["get_action_cfg"](self.config, "release", btn_state.get_keytime())
            if release_cfg:
                self.callbacks["send_action"](release_cfg, self.btn_num, self.idx, "release")
            self.callbacks["set_button_state"](self.btn_num, False)
        elif not self.long_enabled and self.mode != "tap":
            # Standard release for toggle modes without long-press
            if self.mode == "momentary":
                release_cfg = self.callbacks["get_action_cfg"](self.config, "release", btn_state.get_keytime())
                if release_cfg:
                    self.callbacks["send_action"](release_cfg, self.btn_num, self.idx, "release")
                self.callbacks["set_button_state"](self.btn_num, False)
