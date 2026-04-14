import { describe, it, expect } from 'vitest';
import { validators, validateConfig } from './validation';
import { createMidiCaptainConfig, createButtonConfig } from './testUtils';

describe('validators', () => {
	describe('label', () => {
		it('should accept valid labels', () => {
			expect(validators.label('BTN 1')).toBeNull();
			expect(validators.label('Scene')).toBeNull();
			expect(validators.label('A-B C')).toBeNull();
		});

		it('should reject empty labels', () => {
			expect(validators.label('')).toBe('Label is required');
			expect(validators.label('   ')).toBe('Label is required');
		});

		it('should reject labels longer than 6 characters', () => {
			expect(validators.label('TOOLONG')).toBe('Label must be 6 characters or less');
		});

		it('should reject labels with invalid characters', () => {
			expect(validators.label('BTN@1')).toBe('Label contains invalid characters');
			expect(validators.label('BTN#1')).toBe('Label contains invalid characters');
		});
	});

	describe('cc', () => {
		it('should accept valid CC numbers', () => {
			expect(validators.cc(0)).toBeNull();
			expect(validators.cc(64)).toBeNull();
			expect(validators.cc(127)).toBeNull();
		});

		it('should reject CC numbers out of range', () => {
			expect(validators.cc(-1)).toBe('CC must be between 0 and 127');
			expect(validators.cc(128)).toBe('CC must be between 0 and 127');
		});

		it('should reject non-integer CC numbers', () => {
			expect(validators.cc(64.5)).toBe('CC must be an integer');
		});
	});

	describe('channel', () => {
		it('should accept valid channels (0-15)', () => {
			expect(validators.channel(0)).toBeNull();
			expect(validators.channel(7)).toBeNull();
			expect(validators.channel(15)).toBeNull();
		});

		it('should reject channels out of range', () => {
			expect(validators.channel(-1)).toBe('Channel must be between 1 and 16');
			expect(validators.channel(16)).toBe('Channel must be between 1 and 16');
		});

		it('should reject non-integer channels', () => {
			expect(validators.channel(5.5)).toBe('Channel must be an integer');
		});
	});

	describe('note', () => {
		it('should accept valid note numbers', () => {
			expect(validators.note(0)).toBeNull();
			expect(validators.note(60)).toBeNull(); // Middle C
			expect(validators.note(127)).toBeNull();
		});

		it('should reject invalid note numbers', () => {
			expect(validators.note(-1)).toBe('Note must be between 0 and 127');
			expect(validators.note(128)).toBe('Note must be between 0 and 127');
			expect(validators.note(60.5)).toBe('Note must be an integer');
		});
	});

	describe('velocity', () => {
		it('should accept valid velocities', () => {
			expect(validators.velocity(1)).toBeNull();
			expect(validators.velocity(64)).toBeNull();
			expect(validators.velocity(127)).toBeNull();
		});

		it('should reject invalid velocities', () => {
			expect(validators.velocity(-1)).toBe('Velocity must be between 0 and 127');
			expect(validators.velocity(128)).toBe('Velocity must be between 0 and 127');
			expect(validators.velocity(64.5)).toBe('Velocity must be an integer');
		});
	});

	describe('program', () => {
		it('should accept valid program numbers', () => {
			expect(validators.program(0)).toBeNull();
			expect(validators.program(64)).toBeNull();
			expect(validators.program(127)).toBeNull();
		});

		it('should reject invalid program numbers', () => {
			expect(validators.program(-1)).toBe('Program must be between 0 and 127');
			expect(validators.program(128)).toBe('Program must be between 0 and 127');
			expect(validators.program(64.5)).toBe('Program must be an integer');
		});
	});

	describe('pcStep', () => {
		it('should accept valid step sizes', () => {
			expect(validators.pcStep(1)).toBeNull();
			expect(validators.pcStep(10)).toBeNull();
			expect(validators.pcStep(127)).toBeNull();
		});

		it('should reject invalid step sizes', () => {
			expect(validators.pcStep(0)).toBe('Step must be between 1 and 127');
			expect(validators.pcStep(128)).toBe('Step must be between 1 and 127');
			expect(validators.pcStep(5.5)).toBe('Step must be an integer');
		});
	});

	describe('keytimes', () => {
		it('should accept valid keytimes', () => {
			expect(validators.keytimes(1)).toBeNull();
			expect(validators.keytimes(5)).toBeNull();
			expect(validators.keytimes(99)).toBeNull();
		});

		it('should reject invalid keytimes', () => {
			expect(validators.keytimes(0)).toBe('Keytimes must be between 1 and 99');
			expect(validators.keytimes(100)).toBe('Keytimes must be between 1 and 99');
			expect(validators.keytimes(5.5)).toBe('Keytimes must be an integer');
		});
	});

	describe('flashMs', () => {
		it('should accept valid flash durations', () => {
			expect(validators.flashMs(50)).toBeNull();
			expect(validators.flashMs(200)).toBeNull();
			expect(validators.flashMs(5000)).toBeNull();
		});

		it('should reject invalid flash durations', () => {
			expect(validators.flashMs(49)).toBe('Flash duration must be between 50 and 5000 ms');
			expect(validators.flashMs(5001)).toBe('Flash duration must be between 50 and 5000 ms');
			expect(validators.flashMs(200.5)).toBe('Flash duration must be an integer');
		});
	});

	describe('range', () => {
		it('should accept valid ranges', () => {
			expect(validators.range(0, 127)).toBeNull();
			expect(validators.range(10, 100)).toBeNull();
		});

		it('should reject invalid ranges', () => {
			expect(validators.range(100, 10)).toBe('Min must be less than max');
			expect(validators.range(50, 50)).toBe('Min must be less than max');
		});
	});

	describe('withinRange', () => {
		it('should accept values within range', () => {
			expect(validators.withinRange(50, 0, 127)).toBeNull();
			expect(validators.withinRange(0, 0, 127)).toBeNull();
			expect(validators.withinRange(127, 0, 127)).toBeNull();
		});

		it('should reject values outside range', () => {
			expect(validators.withinRange(-1, 0, 127)).toBe('Value must be between 0 and 127');
			expect(validators.withinRange(128, 0, 127)).toBe('Value must be between 0 and 127');
		});
	});
});

describe('validateConfig', () => {
	it('should accept a valid minimal config', () => {
		const config = createMidiCaptainConfig(10);
		const result = validateConfig(config);
		expect(result.isValid).toBe(true);
		expect(result.errors.size).toBe(0);
	});

	it('should detect invalid button labels', () => {
		const config = createMidiCaptainConfig(10, {
			buttons: [createButtonConfig({ label: 'TOOLONG' })]
		});
		const result = validateConfig(config);
		expect(result.isValid).toBe(false);
		expect(result.errors.has('buttons[0].label')).toBe(true);
	});

	it('should detect invalid CC numbers', () => {
		const config = createMidiCaptainConfig(10, {
			buttons: [createButtonConfig({ cc: 200 })]
		});
		const result = validateConfig(config);
		expect(result.isValid).toBe(false);
		expect(result.errors.has('buttons[0].cc')).toBe(true);
	});

	it('should detect invalid channels', () => {
		const config = createMidiCaptainConfig(10, {
			buttons: [createButtonConfig({ channel: 20 })]
		});
		const result = validateConfig(config);
		expect(result.isValid).toBe(false);
		expect(result.errors.has('buttons[0].channel')).toBe(true);
	});

	it('should validate banks in multi-bank mode', () => {
		const config = createMidiCaptainConfig(0, {
			banks: [
				{
					name: 'Bank 1',
					buttons: [createButtonConfig({ label: 'BTN 1' })]
				},
				{
					name: 'Bank 2',
					buttons: [createButtonConfig({ label: 'TOOLONG' })]
				}
			]
		});
		const result = validateConfig(config);
		expect(result.isValid).toBe(false);
		expect(result.errors.has('banks[1].buttons[0].label')).toBe(true);
	});

	describe('multi-command arrays', () => {
		it('should accept valid multi-command press arrays', () => {
			const testButton = createButtonConfig({
				press: [
					{ type: 'cc', cc: 20, value: 127 },
					{ type: 'note', note: 60, velocity: 100 }
				]
			});
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: [testButton, ...Array.from({ length: 5 }, () => createButtonConfig())]
			});
			const result = validateConfig(config);
		expect(result.isValid).toBe(true);
	});

	it('should accept valid multi-command with release arrays', () => {
			const testButton = createButtonConfig({
				press: [{ type: 'cc', cc: 20, value: 127 }],
				release: [{ type: 'cc', cc: 20, value: 0 }]
			});
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: [testButton, ...Array.from({ length: 5 }, () => createButtonConfig())]
			});
			const result = validateConfig(config);
			expect(result.isValid).toBe(true);
		});

		it('should accept PC commands in arrays', () => {
			const testButton = createButtonConfig({
				press: [{ type: 'pc', program: 5, channel: 0 }]
			});
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: [testButton, ...Array.from({ length: 5 }, () => createButtonConfig())]
			});
			const result = validateConfig(config);
			expect(result.isValid).toBe(true);
		});

		it('should accept PC increment/decrement commands', () => {
			const testButton = createButtonConfig({
				press: [{ type: 'pc_inc', pc_step: 1 }]
			});
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: [testButton, ...Array.from({ length: 5 }, () => createButtonConfig())]
			});
			const result = validateConfig(config);
			expect(result.isValid).toBe(true);
		});
	});

	describe('conditional commands', () => {
		it('should accept valid conditional commands with button state', () => {
			const testButtons = [
				createButtonConfig({
					label: 'BTN 1',
					press: [
						{
							type: 'conditional',
							if: {
								type: 'button_state',
								button: 1,
								state: 'on'
							},
							then: [
								{ type: 'cc', cc: 20, value: 127 }
							],
							else: [
								{ type: 'cc', cc: 20, value: 0 }
							],


						}
					]
				}),
				createButtonConfig({ label: 'BTN 2' }),
				...Array.from({ length: 4 }, () => createButtonConfig())
			];
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: testButtons
			});
			const result = validateConfig(config);
			expect(result.isValid).toBe(true);
		});

		it('should accept conditional commands with received MIDI', () => {
			const testButton = createButtonConfig({
				press: [
					{
						type: 'conditional',
						if: {
							type: 'received_midi',
							cc: 22,
							channel: 0,
							operator: '==',
							value: 127
						},
						then: [
							{ type: 'cc', cc: 30, value: 127 }
						],
						else: null,
						then_label: 'Active',

					}
				]
			});
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: [testButton, ...Array.from({ length: 5 }, () => createButtonConfig())]
			});
			const result = validateConfig(config);
			expect(result.isValid).toBe(true);
		});

		it('should accept conditional commands with encoder condition', () => {
			const testButton = createButtonConfig({
				press: [
					{
						type: 'conditional',
						if: {
							type: 'encoder',
							operator: '>',
							value: 64
						},
						then: [
							{ type: 'cc', cc: 40, value: 127 }
						],
						else: null,


					}
				]
			});
			const config = createMidiCaptainConfig(6, {
				device: 'mini6',
				buttons: [testButton, ...Array.from({ length: 5 }, () => createButtonConfig())]
			});
			const result = validateConfig(config);
			expect(result.isValid).toBe(true);
		});
	});
});
