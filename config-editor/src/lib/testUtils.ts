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
		color: 'red',
		type: 'cc',
		mode: 'toggle',
		off_mode: 'dim'
	};

	return { ...defaults, ...overrides };
}

/**
 * Create a MidiCommand with sensible defaults
 */
export function createMidiCommand(overrides?: Partial<MidiCommand>): MidiCommand {
	const defaults: MidiCommand = {
		type: 'cc',
		cc: 20,
		value: 127
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
		else: [createMidiCommand({ value: 0 })]
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
		buttons
	};

	return { ...defaults, ...overrides };
}

/**
 * Create a mini6 config (6 buttons)
 */
export function createMini6Config(overrides?: Partial<MidiCaptainConfig>): MidiCaptainConfig {
	return createMidiCaptainConfig(6, { device: 'mini6', ...overrides });
}
