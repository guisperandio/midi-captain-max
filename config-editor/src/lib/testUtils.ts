/**
 * Test utilities and fixtures for config editor tests
 */

import type { ButtonConfig, MidiCaptainConfig, MidiCommand, ConditionalCommand, Condition } from './types';

/**
 * Create a ButtonConfig with sensible defaults
 * All required fields are provided, overrides can customize
 */
export function createButtonConfig(overrides?: Partial<ButtonConfig>): ButtonConfig {
	const defaults: ButtonConfig = {
		label: 'BTN 1',
		long_press_label: null,
		long_press_color: null,
		long_press_label_persist: null,
		conditional_label_persist: null,
		color: 'red',
		profile_id: null,
		action_id: null,
		press: null,
		release: null,
		long_press: null,
		long_release: null,
		double_press: null,
		double_press_timeout_ms: null,
		message_type: 'cc',
		mode: 'toggle',
		off_mode: 'dim',
		dim_brightness: null,
		channel: null,
		cc: null,
		cc_on: null,
		cc_off: null,
		note: null,
		velocity_on: null,
		velocity_off: null,
		program: null,
		pc_step: null,
		flash_ms: null,
		value_on: null,
		value_off: null,
		default_on: null,
		keytimes: null,
		states: null,
		select_group: null,
		default_selected: null
	};

	return { ...defaults, ...overrides };
}

/**
 * Create a MidiCommand with sensible defaults
 */
export function createMidiCommand(overrides?: Partial<MidiCommand>): MidiCommand {
	const defaults: MidiCommand = {
		type: 'cc',
		channel: null,
		cc: 20,
		value: 127,
		note: null,
		velocity: null,
		program: null,
		pc_step: null,
		threshold_ms: null
	};

	return { ...defaults, ...overrides };
}

/**
 * Create a Condition for conditional commands
 */
export function createCondition(type: 'button_state'): Condition {
	return {
		type: 'button_state',
		button: 0,
		state: 'on'
	};
}

/**
 * Create a ConditionalCommand with sensible defaults
 */
export function createConditionalCommand(
	overrides?: Partial<ConditionalCommand>
): ConditionalCommand {
	const defaults: ConditionalCommand = {
		type: 'conditional',
		if: createCondition('button_state'),
		then: [createMidiCommand({ value: 127 })],
		else: [createMidiCommand({ value: 0 })],
		then_label: null,
		else_label: null
	};

	return { ...defaults, ...overrides };
}

/**
 * Create a complete MidiCaptainConfig with sensible defaults
 * @param buttonCount Number of buttons to create (default: 10 for std10)
 */
export function createMidiCaptainConfig(
	buttonCount: number = 10,
	overrides?: Partial<MidiCaptainConfig>
): MidiCaptainConfig {
	const buttons: ButtonConfig[] = Array.from({ length: buttonCount }, (_, i) =>
		createButtonConfig({ label: `BTN ${i + 1}` })
	);

	const defaults: MidiCaptainConfig = {
		device: 'std10',
		global_channel: null,
		usb_drive_name: null,
		dev_mode: null,
		midi_transport: null,
		banks: null,
		bank_switch: null,
		active_bank: null,
		buttons,
		encoder: null,
		expression: null,
		display: null,
		splash_screen: null,
		long_press_threshold_ms: null,
		double_press_timeout_ms: null,
		channel_labels: null
	};

	return { ...defaults, ...overrides };
}

/**
 * Create a mini6 config (6 buttons)
 */
export function createMini6Config(overrides?: Partial<MidiCaptainConfig>): MidiCaptainConfig {
	return createMidiCaptainConfig(6, { device: 'mini6', ...overrides });
}
