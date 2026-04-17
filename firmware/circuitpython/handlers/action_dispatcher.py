"""
Action dispatcher for MIDI command execution.

Handles dispatching MIDI commands from button actions (press, release, long_press, etc.)
with support for:
- Multiple commands per action
- Conditional logic (if/then/else)
- Label management (normal, long_press, conditional)
- Command types: CC, Note, PC, PC+, PC-

Extracted from monolithic code.py to improve modularity and testability.

Author: Phase 4 refactoring - code.py reduction
Date: 2026-04-14
"""

import time
from core.condition_evaluator import ConditionEvaluator


class _SnapState:
    """Lightweight stand-in for ButtonState used by conditional evaluation.

    Holds a snapshot of a button's on/off state captured at press-down time
    so the conditional evaluator sees pre-press state.
    """
    __slots__ = ('state', 'current_keytime')

    def __init__(self, st=False):
        # type: (bool) -> None
        self.state = st
        self.current_keytime = 1

    def get_keytime(self):
        # type: () -> int
        return self.current_keytime


class ActionDispatcher:
    """
    Handles MIDI command dispatch from button action configurations.

    Supports single commands, multiple commands, and conditional logic.
    Manages display label updates for normal, long_press, and conditional actions.
    """

    def __init__(self, device_state, buttons, callbacks, display_refs, midi_msgs, feature_flags, constants):
        # type: (object, list, dict, dict, dict, dict, dict) -> None
        """
        Initialize action dispatcher.

        Args:
            device_state: DeviceState instance (holds button_states, pc_values, etc.)
            buttons: List of button configuration dicts
            callbacks: Dict of callback functions:
                - send_midi_message: (msg, channel) -> None
                - set_label_text: (label, text) -> None
                - arm_label_return_timeout: (btn_config) -> None
                - set_label_timeout: (timeout) -> None
                - clamp_pc_value: (value) -> int
                - flash_pc_button: (btn_num, flash_ms) -> None
                - get_button_state_config: (btn_config, keytime) -> dict
            display_refs: Dict with display label references:
                - button_name_label: Label object for button name
                - status_label: Label object for status text
            midi_msgs: Dict with MIDI message objects:
                - cc: ControlChange message (reused for performance)
                - note_on: NoteOn message (reused for performance)
                - note_off: NoteOff message (reused for performance)
                - pc: ProgramChange message (reused for performance)
                - sysex: SystemExclusive constructor class (creates new instances)
            feature_flags: Dict with hardware feature flags:
                - HAS_EXPRESSION: bool
                - HAS_ENCODER: bool
            constants: Dict with firmware constants:
                - LABEL_RETURN_TIMEOUT_SEC: float
                - INTER_COMMAND_DELAY_SEC: float
        """
        # Validate required callbacks
        required_callbacks = [
            "send_midi_message", "set_label_text", "arm_label_return_timeout",
            "set_label_timeout", "clamp_pc_value", "flash_pc_button", "get_button_state_config"
        ]
        for cb_name in required_callbacks:
            if cb_name not in callbacks:
                raise ValueError("Missing required callback: {}".format(cb_name))
        
        # Validate required display refs
        required_display_refs = ["button_name_label", "status_label"]
        for ref_name in required_display_refs:
            if ref_name not in display_refs:
                raise ValueError("Missing required display_ref: {}".format(ref_name))
        
        # Validate required MIDI messages
        required_midi_msgs = ["cc", "note_on", "note_off", "pc", "sysex"]
        for msg_name in required_midi_msgs:
            if msg_name not in midi_msgs:
                raise ValueError("Missing required midi_msg: {}".format(msg_name))
        
        # Validate required constants
        required_constants = ["LABEL_RETURN_TIMEOUT_SEC", "INTER_COMMAND_DELAY_SEC"]
        for const_name in required_constants:
            if const_name not in constants:
                raise ValueError("Missing required constant: {}".format(const_name))
        
        self.device_state = device_state
        self.buttons = buttons
        self.callbacks = callbacks
        self.display_refs = display_refs
        self.midi_msgs = midi_msgs
        self.feature_flags = feature_flags
        self.constants = constants

    def send_action(self, action_cfg, btn_num, idx, action_name=None, skip_label_update=False):
        # type: (object, int, int, str, bool) -> None
        """
        Send MIDI from action config (single dict or list of dicts).

        Args:
            action_cfg: Single command dict or list of command dicts
            btn_num: 1-indexed button number
            idx: 0-indexed button index
            action_name: Optional action type ("press", "release", "long_press", "long_release")
                         Used to display long_press_label when available
            skip_label_update: Skip updating the display label (used for conditional branches)

        Supports:
        - Single command: {"type":"cc","cc":20,"value":127,"channel":0}
        - Multiple commands: [{"type":"cc",...}, {"type":"pc",...}]

        Command types: cc, note, pc, pc_inc, pc_dec, sysex, conditional
        """
        if not action_cfg:
            return

        # Normalize to list
        if isinstance(action_cfg, dict):
            commands = [action_cfg]
        elif isinstance(action_cfg, list):
            commands = action_cfg
        else:
            print(f"[WARN] Invalid action_cfg type (button {btn_num}): {type(action_cfg)}")
            return

        # Display button name in center (large font)
        btn_config = self.buttons[idx] if idx < len(self.buttons) else {}

        # Skip label update if we're inside a conditional branch
        # (the conditional handler has already set the appropriate label)
        if not skip_label_update:
            print(f"[LABEL] Setting label for action={action_name}, skip={skip_label_update}")
            # For long_press actions: only update label if long_press_label is configured
            # Otherwise, keep the current display (likely showing the selected button)
            if action_name == "long_press":
                if "long_press_label" in btn_config:
                    # Long press label configured - show it
                    label_text = btn_config.get("long_press_label")
                    print(f"[LABEL] Setting long_press_label: '{label_text}'")
                    self.callbacks["set_label_text"](self.display_refs["button_name_label"], label_text)

                    # Check if label should persist or timeout
                    persist = btn_config.get("long_press_label_persist", True)
                    if not persist:
                        # Override select_group logic: force timeout even for select buttons
                        self.callbacks["set_label_timeout"](
                            time.monotonic() + self.constants["LABEL_RETURN_TIMEOUT_SEC"]
                        )
                    else:
                        # Use normal logic (select buttons stay, others timeout)
                        self.callbacks["arm_label_return_timeout"](btn_config)
                else:
                    # No long_press_label configured - don't change the display
                    # Keep showing whatever was there (likely the selected button's label)
                    print("[LABEL] No long_press_label configured, keeping current display")
                    pass
            else:
                # Normal press/release action - always show button label (with per-state override if applicable)
                state_cfg = self.callbacks["get_button_state_config"](
                    btn_config,
                    self.device_state.button_states[idx].get_keytime()
                )
                label_text = state_cfg.get("label", str(btn_num))
                print(f"[LABEL] Setting button label: '{label_text}'")
                self.callbacks["set_label_text"](self.display_refs["button_name_label"], label_text)
                self.callbacks["arm_label_return_timeout"](btn_config)
        else:
            print("[LABEL] Skipping label update (skip_label_update=True)")

        # Track if any PC command executed (for LED flash feedback)
        pc_command_sent = False

        # Execute each command in sequence
        for cmd_idx, cmd in enumerate(commands):
            if not isinstance(cmd, dict):
                print(f"[WARN] Invalid command in action (button {btn_num}): {cmd}")
                continue

            # Small delay between commands for MIDI buffer management (MIDI Thru chains)
            # Skip delay before first command for immediate response
            if cmd_idx > 0:
                time.sleep(self.constants["INTER_COMMAND_DELAY_SEC"])

            msg_type = cmd.get("type", "cc")
            channel = cmd.get("channel", 0)

            # Handle conditional commands (if/then/else logic)
            if msg_type == "conditional":
                pc_command_sent = self._handle_conditional(
                    cmd, btn_num, idx, btn_config, action_name
                ) or pc_command_sent
                continue

            # Send MIDI command
            sent_pc = self._send_midi_command(cmd, msg_type, channel, btn_num, idx)
            pc_command_sent = pc_command_sent or sent_pc

        # Flash LED once if any PC command was sent in this action
        # BUT skip flash if long_press is active - preserve long_press_color instead
        if pc_command_sent and action_name != "long_press":
            self.callbacks["flash_pc_button"](btn_num, None)

    def _handle_conditional(self, cmd, btn_num, idx, btn_config, action_name):
        # type: (dict, int, int, dict, str) -> bool
        """
        Handle conditional command (if/then/else logic).

        Returns:
            True if any PC command was sent in the conditional branch
        """
        print(f"[CONDITIONAL] Raw cmd dict keys: {list(cmd.keys())}")
        print(f"[CONDITIONAL] Full cmd dict: {cmd}")

        condition = cmd.get("if")
        then_commands = cmd.get("then", [])
        else_commands = cmd.get("else", [])

        if not condition:
            print(f"[WARN] Conditional command missing 'if' condition (button {btn_num})")
            return False

        # Prepare evaluator inputs
        has_expression = self.feature_flags.get("HAS_EXPRESSION", False)
        has_encoder = self.feature_flags.get("HAS_ENCODER", False)
        
        exp_vals = {}
        if has_expression:
            exp_vals['exp1'] = self.device_state.exp1_last
            exp_vals['exp2'] = self.device_state.exp2_last
        else:
            exp_vals['exp1'] = 0
            exp_vals['exp2'] = 0

        enc_val = self.device_state.encoder_value if has_encoder else 64

        # Use snapshot for button_state conditions when available
        use_snapshot = (condition.get('type') == 'button_state' and
                       0 <= idx < len(self.device_state.state_at_press) and
                       self.device_state.state_at_press[idx] is not None)

        if use_snapshot:
            snap_states = []
            snap = self.device_state.state_at_press[idx]
            for si in range(len(self.device_state.button_states)):
                s = _SnapState(snap['states'][si])
                s.current_keytime = snap['keytimes'][si]
                snap_states.append(s)
        else:
            snap_states = self.device_state.button_states

        evaluator = ConditionEvaluator(
            button_states=snap_states,
            received_cc_values=self.device_state.received_cc_values,
            encoder_value=enc_val,
            expression_values=exp_vals,
        )

        # Evaluate condition
        condition_result = evaluator.evaluate(condition)

        # Get labels for conditional branches (optional)
        then_label = cmd.get("then_label")
        else_label = cmd.get("else_label")
        # Check if conditional labels should persist or timeout
        conditional_persist = btn_config.get("conditional_label_persist", False)

        print(f"[CONDITIONAL] then_label={then_label}, else_label={else_label}, persist={conditional_persist}")

        # Execute appropriate branch and track if PC commands were sent
        pc_command_sent = False
        
        if condition_result:
            print(f"[CONDITIONAL] Condition TRUE (button {btn_num}), executing THEN branch with {len(then_commands)} command(s)")
            if then_label:
                print(f"[CONDITIONAL] Setting THEN label: '{then_label}'")
                self.callbacks["set_label_text"](self.display_refs["button_name_label"], then_label)
                # Only arm timeout if persist is disabled
                if not conditional_persist:
                    self.callbacks["arm_label_return_timeout"](btn_config)
            else:
                print("[CONDITIONAL] No THEN label configured")
            # Track PC commands from then branch
            pc_command_sent = self._dispatch_commands_recursive(then_commands, btn_num, idx, action_name)
        else:
            print(f"[CONDITIONAL] Condition FALSE (button {btn_num}), executing ELSE branch with {len(else_commands)} command(s)")
            if else_label:
                print(f"[CONDITIONAL] Setting ELSE label: '{else_label}'")
                self.callbacks["set_label_text"](self.display_refs["button_name_label"], else_label)
                # Only arm timeout if persist is disabled
                if not conditional_persist:
                    self.callbacks["arm_label_return_timeout"](btn_config)
            else:
                print("[CONDITIONAL] No ELSE label configured")
            # Track PC commands from else branch
            pc_command_sent = self._dispatch_commands_recursive(else_commands, btn_num, idx, action_name)

        return pc_command_sent

    def _send_midi_command(self, cmd, msg_type, channel, btn_num, idx):
        # type: (dict, str, int, int, int) -> bool
        """
        Send a single MIDI command.

        Returns:
            True if a PC-type command was sent (for LED flash tracking)
        """
        try:
            if msg_type == "cc":
                cc = cmd.get("cc", 20 + idx)
                val = cmd.get("value", cmd.get("cc_on", 127))
                # Reuse message object for performance (avoid allocation)
                self.midi_msgs["cc"].control = cc
                self.midi_msgs["cc"].value = val
                self.callbacks["send_midi_message"](self.midi_msgs["cc"], channel=channel)
                print(f"[MIDI TX] Ch{channel+1} CC{cc}={val} (switch {btn_num})")
                self.callbacks["set_label_text"](self.display_refs["status_label"], f"TX CC{cc}={val}")
                return False

            elif msg_type == "note":
                note = cmd.get("note", 60)
                vel = cmd.get("velocity", cmd.get("velocity_on", 127))
                # Reuse message object for performance (avoid allocation)
                self.midi_msgs["note_on"].note = note
                self.midi_msgs["note_on"].velocity = vel
                self.callbacks["send_midi_message"](self.midi_msgs["note_on"], channel=channel)
                print(f"[MIDI TX] Ch{channel+1} NoteOn{note} vel{vel} (switch {btn_num})")
                self.callbacks["set_label_text"](self.display_refs["status_label"], f"TX Note{note}")
                return False

            elif msg_type == "pc":
                program = cmd.get("program", 0)
                # Reuse message object for performance (avoid allocation)
                self.midi_msgs["pc"].patch = program
                self.callbacks["send_midi_message"](self.midi_msgs["pc"], channel=channel)
                print(f"[MIDI TX] Ch{channel+1} PC{program} (switch {btn_num})")
                self.callbacks["set_label_text"](self.display_refs["status_label"], f"TX PC{program}")
                return True  # PC command sent

            elif msg_type == "pc_inc":
                step = cmd.get("pc_step", 1)
                self.device_state.pc_values[channel] = self.callbacks["clamp_pc_value"](
                    self.device_state.pc_values[channel] + step
                )
                # Reuse message object for performance (avoid allocation)
                self.midi_msgs["pc"].patch = self.device_state.pc_values[channel]
                self.callbacks["send_midi_message"](self.midi_msgs["pc"], channel=channel)
                print(f"[MIDI TX] Ch{channel+1} PC{self.device_state.pc_values[channel]} +{step} (switch {btn_num})")
                self.callbacks["set_label_text"](self.display_refs["status_label"], f"TX PC{self.device_state.pc_values[channel]}")
                return True  # PC command sent

            elif msg_type == "pc_dec":
                step = cmd.get("pc_step", 1)
                self.device_state.pc_values[channel] = self.callbacks["clamp_pc_value"](
                    self.device_state.pc_values[channel] - step
                )
                # Reuse message object for performance (avoid allocation)
                self.midi_msgs["pc"].patch = self.device_state.pc_values[channel]
                self.callbacks["send_midi_message"](self.midi_msgs["pc"], channel=channel)
                print(f"[MIDI TX] Ch{channel+1} PC{self.device_state.pc_values[channel]} -{step} (switch {btn_num})")
                self.callbacks["set_label_text"](self.display_refs["status_label"], f"TX PC{self.device_state.pc_values[channel]}")
                return True  # PC command sent

            elif msg_type == "sysex":
                # Parse hex string data (format: "F0 7F 7F 06 02 F7")
                hex_data = cmd.get("data", "")
                if not hex_data:
                    print(f"[WARN] SysEx command missing 'data' field (button {btn_num})")
                    return False
                
                try:
                    # Parse hex string into bytes
                    hex_bytes = [int(x, 16) for x in hex_data.split()]
                    
                    # Validate format: must start with F0 and end with F7
                    if len(hex_bytes) < 2 or hex_bytes[0] != 0xF0 or hex_bytes[-1] != 0xF7:
                        print(f"[WARN] Invalid SysEx format (must start with F0, end with F7): {hex_data}")
                        return False
                    
                    # Extract manufacturer ID (1-3 bytes after F0, before data)
                    # Standard: single byte (e.g., 0x7F for universal)
                    # Extended: 3 bytes starting with 0x00 (e.g., 0x00 0x01 0x78 for NDSP Quad Cortex)
                    if hex_bytes[1] == 0x00 and len(hex_bytes) >= 5:
                        # Extended manufacturer ID (3 bytes)
                        manufacturer_id = hex_bytes[1:4]
                        data_bytes = hex_bytes[4:-1]  # Between manufacturer ID and F7
                    else:
                        # Standard manufacturer ID (1 byte)
                        manufacturer_id = [hex_bytes[1]]
                        data_bytes = hex_bytes[2:-1]  # Between manufacturer ID and F7
                    
                    # Create and send SystemExclusive message
                    # Note: SystemExclusive constructor, not a reusable message object
                    sysex_msg = self.midi_msgs["sysex"](manufacturer_id=manufacturer_id, data=data_bytes)
                    self.callbacks["send_midi_message"](sysex_msg, channel=0)  # SysEx ignores channel
                    
                    # Format for display (show first few bytes)
                    display_data = ' '.join(f'{b:02X}' for b in hex_bytes[:6])
                    if len(hex_bytes) > 6:
                        display_data += '...'
                    print(f"[MIDI TX] SysEx: {hex_data} (switch {btn_num})")
                    self.callbacks["set_label_text"](self.display_refs["status_label"], f"TX SysEx {display_data}")
                    return False
                
                except (ValueError, IndexError) as e:
                    print(f"[ERROR] Failed to parse SysEx data '{hex_data}': {e}")
                    return False

            else:
                print(f"[WARN] Unknown command type '{msg_type}' (button {btn_num})")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to send command (button {btn_num}): {e}")
            # Continue to next command
            return False
    
    def _dispatch_commands_recursive(self, commands, btn_num, idx, action_name):
        # type: (list, int, int, str) -> bool
        """
        Recursively dispatch commands (for conditional branches).
        
        Args:
            commands: List of command dicts to execute
            btn_num: 1-indexed button number
            idx: 0-indexed button index
            action_name: Action type name
        
        Returns:
            True if any PC command was sent
        """
        if not commands:
            return False
        
        # Normalize to list
        if isinstance(commands, dict):
            commands = [commands]
        elif not isinstance(commands, list):
            return False
        
        pc_command_sent = False
        
        for cmd_idx, cmd in enumerate(commands):
            if not isinstance(cmd, dict):
                continue
            
            # Small delay between commands (skip first)
            if cmd_idx > 0:
                time.sleep(self.constants["INTER_COMMAND_DELAY_SEC"])
            
            msg_type = cmd.get("type", "cc")
            channel = cmd.get("channel", 0)
            
            # Handle nested conditionals (thread through original button config)
            if msg_type == "conditional":
                # Get original button config for consistent label timeout behavior
                orig_btn_config = self.buttons[idx] if idx < len(self.buttons) else {}
                pc_sent = self._handle_conditional(cmd, btn_num, idx, orig_btn_config, action_name)
                pc_command_sent = pc_command_sent or pc_sent
            else:
                # Send MIDI command
                pc_sent = self._send_midi_command(cmd, msg_type, channel, btn_num, idx)
                pc_command_sent = pc_command_sent or pc_sent
        
        return pc_command_sent
