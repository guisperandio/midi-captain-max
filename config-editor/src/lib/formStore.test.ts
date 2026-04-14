import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { get } from 'svelte/store';
import {
	formState,
	config,
	isDirty,
	canUndo,
	canRedo,
	loadConfig,
	updateField,
	undo,
	redo,
	normalizeConfig
} from './formStore';
import { createMidiCaptainConfig, createButtonConfig } from './testUtils';

describe('formStore', () => {
	beforeEach(() => {
		vi.useFakeTimers();
		// Reset to clean state before each test
		loadConfig(createMidiCaptainConfig(10));
	});

	afterEach(() => {
		vi.clearAllTimers();
		vi.useRealTimers();
	});

	describe('loadConfig', () => {
		it('should load a config and reset history', () => {
			const testConfig = createMidiCaptainConfig(5);
			loadConfig(testConfig);

			const currentConfig = get(config);
			expect(currentConfig.device).toBe('std10');
			// Config auto-migrates buttons to banks[0].buttons
			expect(currentConfig.banks?.[0]?.buttons?.length).toBe(5);
			expect(get(isDirty)).toBe(false);
			expect(get(canUndo)).toBe(false);
			expect(get(canRedo)).toBe(false);
		});

		it('should auto-migrate legacy single-bank format', () => {
			const legacyConfig = createMidiCaptainConfig(3);
			loadConfig(legacyConfig);

			const currentConfig = get(config);
			// Should have migrated buttons to banks[0]
			expect(currentConfig.banks).toBeDefined();
			expect(currentConfig.banks?.length).toBe(1);
			expect(currentConfig.banks?.[0].buttons.length).toBe(3);
			expect(currentConfig.buttons).toBeUndefined();
		});

		it('should initialize display object if missing', () => {
			const configWithoutDisplay = createMidiCaptainConfig(1, { display: undefined });
			loadConfig(configWithoutDisplay);

			const currentConfig = get(config);
			expect(currentConfig.display).toBeDefined();
		});

		it('should set active_bank from config', () => {
			const configWithBank = createMidiCaptainConfig(0, {
				banks: [
					{ name: 'Bank 1', buttons: [createButtonConfig()] },
					{ name: 'Bank 2', buttons: [createButtonConfig()] }
				],
				active_bank: 1
			});
			loadConfig(configWithBank);

			const currentConfig = get(config);
			expect(currentConfig.active_bank).toBe(1);
		});
	});

	describe('updateField', () => {
		it('should update a top-level field', () => {
			updateField('device', 'mini6');

			const currentConfig = get(config);
			expect(currentConfig.device).toBe('mini6');
			expect(get(isDirty)).toBe(true);
		});

		it('should update a button field with array index notation', () => {
			updateField('banks[0].buttons[0].label', 'TEST');

			const currentConfig = get(config);
			expect(currentConfig.banks?.[0].buttons[0].label).toBe('TEST');
		});

		it('should update nested fields', () => {
			// First ensure display exists
			updateField('display.button_text_size', 'large');

			const currentConfig = get(config);
			expect(currentConfig.display?.button_text_size).toBe('large');
		});

		it('should update fields in banks[].buttons[]', () => {
			const configWithBanks = createMidiCaptainConfig(0, {
				banks: [
					{
						name: 'Bank 1',
						buttons: [createButtonConfig({ label: 'OLD' })]
					}
				]
			});
			loadConfig(configWithBanks);

			updateField('banks[0].buttons[0].label', 'NEW');

			const currentConfig = get(config);
			expect(currentConfig.banks?.[0].buttons[0].label).toBe('NEW');
		});

		it('should throw on invalid path', () => {
			expect(() => {
				updateField('nonexistent[0].field', 'value');
			}).toThrow('Invalid path');
		});

		it('should throw on out of bounds array index', () => {
			expect(() => {
				updateField('banks[0].buttons[999].label', 'TEST');
			}).toThrow('out of bounds');
		});

		it('should create nested objects for missing intermediate paths', () => {
			// display might not have button_text_size initially
			updateField('display.button_text_size', 'medium');

			const currentConfig = get(config);
			expect(currentConfig.display?.button_text_size).toBe('medium');
		});
	});

	describe('undo/redo', () => {
		it('should undo a change', () => {
			const original = get(config).banks?.[0].buttons[0].label;

			updateField('banks[0].buttons[0].label', 'CHANGED');
			vi.runAllTimers(); // Flush debounce
			expect(get(config).banks?.[0].buttons[0].label).toBe('CHANGED');

			undo();
			expect(get(config).banks?.[0].buttons[0].label).toBe(original);
			expect(get(canRedo)).toBe(true);
		});

		it('should redo an undone change', () => {
			updateField('banks[0].buttons[0].label', 'CHANGED');
			undo();

			redo();
			expect(get(config).banks?.[0].buttons[0].label).toBe('CHANGED');
		});

		it('should not undo past initial state', () => {
			const initialState = get(config);

			undo(); // Should do nothing
			expect(get(config)).toEqual(initialState);
			expect(get(canUndo)).toBe(false);
		});

		it('should not redo when at latest state', () => {
			updateField('banks[0].buttons[0].label', 'CHANGED');
			const latest = get(config);

			redo(); // Should do nothing
			expect(get(config)).toEqual(latest);
			expect(get(canRedo)).toBe(false);
		});

		it('should clear redo history when making a new change after undo', () => {
			updateField('banks[0].buttons[0].label', 'FIRST');
			vi.runAllTimers(); // Flush first change
			updateField('banks[0].buttons[0].label', 'SECOND');
			vi.runAllTimers(); // Flush second change

			undo(); // Back to FIRST
			expect(get(canRedo)).toBe(true);

			updateField('banks[0].buttons[0].label', 'THIRD'); // New branch
			vi.runAllTimers(); // Flush third change
			expect(get(canRedo)).toBe(false); // Redo history cleared
		});

		it('should maintain history limit of 50 items', () => {
			// Make 60 changes
			for (let i = 0; i < 60; i++) {
				updateField('banks[0].buttons[0].label', `CHANGE${i}`);
			}

			const state = get(formState);
			expect(state.history.length).toBeLessThanOrEqual(50);
		});
	});

	describe('normalizeConfig', () => {
		it('should strip legacy single-type fields from buttons', () => {
			const configWithLegacy = createMidiCaptainConfig(1, {
				buttons: [
					createButtonConfig({
						type: 'cc',
						cc: 20,
						cc_on: 127,
						cc_off: 0,
						note: 60,
						velocity_on: 100,
						velocity_off: 0,
						program: 5,
						pc_step: 1,
						flash_ms: 200,
						// Also has new format
						press: [
							{ type: 'cc', cc: 30, value: 127 }
						]
					} as any)
				]
			});

			const normalized = normalizeConfig(configWithLegacy);
			const button = normalized.buttons?.[0];

			//Legacy fields should be removed if press array exists
			expect(button).toBeDefined();
			if (button) {
				expect(button.message_type).toBeUndefined();
				expect(button.cc).toBeUndefined();
				expect(button.cc_on).toBeUndefined();
				expect(button.cc_off).toBeUndefined();
				expect(button.note).toBeUndefined();
				expect(button.velocity_on).toBeUndefined();
				expect(button.velocity_off).toBeUndefined();
				expect(button.program).toBeUndefined();
				expect(button.pc_step).toBeUndefined();
				expect(button.flash_ms).toBeUndefined();

				// New format preserved
				expect(button.press).toBeDefined();
			}
		});

		it('should strip empty display object', () => {
			const configWithEmptyDisplay = createMidiCaptainConfig(1, {
				display: {}
			});

			const normalized = normalizeConfig(configWithEmptyDisplay);
			expect(normalized.display).toBeUndefined();
		});

		it('should keep display object if it has fields', () => {
			const configWithDisplay = createMidiCaptainConfig(1, {
				display: { button_text_size: 'large' }
			});

			const normalized = normalizeConfig(configWithDisplay);
			expect(normalized.display).toBeDefined();
			expect(normalized.display?.button_text_size).toBe('large');
		});

		it('should preserve keytimes and states', () => {
			const configWithKeytimes = createMidiCaptainConfig(1, {
				buttons: [
					createButtonConfig({
						keytimes: 3,
						states: [
							{ label: 'State 1', cc: 20 }
						]
					})
				]
			});

			const normalized = normalizeConfig(configWithKeytimes);
			const button = normalized.buttons?.[0];

			expect(button?.keytimes).toBe(3);
			expect(button?.states).toBeDefined();
			expect(button?.states?.length).toBe(1);
		});

		it('should preserve select_group and default_selected', () => {
			const configWithSelectGroup = createMidiCaptainConfig(1, {
				buttons: [
					createButtonConfig({
						select_group: 'scenes',
						default_selected: true
					})
				]
			});

			const normalized = normalizeConfig(configWithSelectGroup);
			const button = normalized.buttons?.[0];

			expect(button?.select_group).toBe('scenes');
			expect(button?.default_selected).toBe(true);
		});
	});

	describe('isDirty tracking', () => {
		it('should be clean after loadConfig', () => {
			loadConfig(createMidiCaptainConfig(1));
			expect(get(isDirty)).toBe(false);
		});

		it('should be dirty after updateField', () => {
			updateField('device', 'mini6');
			expect(get(isDirty)).toBe(true);
		});

		it('should be clean after undoing to initial state', () => {
			updateField('device', 'mini6');
			vi.runAllTimers(); // Flush change
			expect(get(isDirty)).toBe(true);

			undo();
			expect(get(isDirty)).toBe(false);
		});

		it('should be dirty after redo', () => {
			updateField('device', 'mini6');
			undo();

			redo();
			expect(get(isDirty)).toBe(true);
		});
	});
});
