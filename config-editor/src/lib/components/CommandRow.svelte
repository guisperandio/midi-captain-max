<script lang="ts">
  import { config } from '$lib/formStore';
  import { formatChannel } from '$lib/utils';
  import type { CommandOrConditional, MidiCommand, MessageType } from '$lib/types';
  import ConditionalCommandBlock from './ConditionalCommandBlock.svelte';

  interface Props {
    command: CommandOrConditional;
    index: number;
    globalChannel: number;
    onUpdate: (cmd: CommandOrConditional) => void;
    onRemove: () => void;
    buttonIndex?: number;
  }

  let { command, index, globalChannel, onUpdate, onRemove, buttonIndex }: Props = $props();

  // Check if this is a conditional command
  let isConditional = $derived(
    typeof command === 'object' &&
    'type' in command &&
    command.type === 'conditional'
  );

  // Generate channel options with labels
  // Include "Use Global" option to allow inheriting global channel
  let channelOptions = $derived([
    { value: 'global', label: `Use Global (${formatChannel(globalChannel, $config)})` },
    ...Array.from({ length: 16 }, (_, i) => ({
      value: i,
      label: formatChannel(i, $config)
    }))
  ]);

  function updateMidiField(field: string, value: any) {
    if (!isConditional) {
      onUpdate({ ...command as MidiCommand, [field]: value });
    }
  }

  function numVal(e: Event): number | undefined {
    const v = (e.target as HTMLInputElement).value;
    return v === '' ? undefined : parseInt(v);
  }
</script>

{#if isConditional}
  <!-- Recursive: Conditional command -->
  <ConditionalCommandBlock
    conditional={command as any}
    globalChannel={globalChannel}
    onUpdate={onUpdate}
    onRemove={onRemove}
    buttonIndex={buttonIndex}
  />
{:else}
  <!-- Base case: Regular MIDI command -->
  <div class="command-row">
    <span class="command-number">{index + 1}</span>

    <div class="command-fields">
      <div class="field">
        <label>Type</label>
        <select value={(command as MidiCommand).type ?? 'cc'} onchange={(e) => updateMidiField('type', (e.target as HTMLSelectElement).value as MessageType)}>
          <option value="cc">CC</option>
          <option value="note">Note</option>
          <option value="pc">PC</option>
          <option value="pc_inc">PC+</option>
          <option value="pc_dec">PC-</option>
          <option value="sysex">SysEx</option>
        </select>
      </div>

      {#if ((command as MidiCommand).type ?? 'cc') === 'cc'}
        <div class="field">
          <label>CC#</label>
          <input type="number" min="0" max="127"
            value={(command as MidiCommand).cc ?? ''} placeholder="20"
            onblur={(e) => updateMidiField('cc', numVal(e))} />
        </div>
        <div class="field">
          <label>Value</label>
          <input type="number" min="0" max="127"
            value={(command as MidiCommand).value ?? ''} placeholder="127"
            onblur={(e) => updateMidiField('value', numVal(e))} />
        </div>
      {:else if ((command as MidiCommand).type ?? 'cc') === 'note'}
        <div class="field">
          <label>Note</label>
          <input type="number" min="0" max="127"
            value={(command as MidiCommand).note ?? ''} placeholder="60"
            onblur={(e) => updateMidiField('note', numVal(e))} />
        </div>
        <div class="field">
          <label>Velocity</label>
          <input type="number" min="0" max="127"
            value={(command as MidiCommand).velocity ?? ''} placeholder="127"
            onblur={(e) => updateMidiField('velocity', numVal(e))} />
        </div>
      {:else if ((command as MidiCommand).type ?? 'cc') === 'pc'}
        <div class="field">
          <label>Program</label>
          <input type="number" min="0" max="127"
            value={(command as MidiCommand).program ?? ''} placeholder="0"
            onblur={(e) => updateMidiField('program', numVal(e))} />
        </div>
      {:else if ((command as MidiCommand).type ?? 'cc') === 'pc_inc' || ((command as MidiCommand).type ?? 'cc') === 'pc_dec'}
        <div class="field">
          <label>Step</label>
          <input type="number" min="1" max="127"
            value={(command as MidiCommand).pc_step ?? ''} placeholder="1"
            onblur={(e) => updateMidiField('pc_step', numVal(e))} />
        </div>
      {:else if ((command as MidiCommand).type ?? 'cc') === 'sysex'}
        <div class="field sysex-data">
          <label>
            Hex Data (F0...F7)
            <span class="info-icon" data-tooltip="Space-separated hex bytes. Examples: MMC Play, Kemper, MPC commands. See docs/SYSEX-EXAMPLES.md for more.">ⓘ</span>
          </label>
          <input type="text"
            value={(command as MidiCommand).data ?? ''}
            placeholder="F0 7F 7F 06 02 F7"
            onblur={(e) => updateMidiField('data', (e.target as HTMLInputElement).value)}
            class="sysex-input" />
        </div>
      {/if}

      <div class="field channel-field">
        <label>Channel</label>
        <select
          value={(command as MidiCommand).channel !== undefined ? (command as MidiCommand).channel : 'global'}
          disabled={((command as MidiCommand).type ?? 'cc') === 'sysex'}
          title={((command as MidiCommand).type ?? 'cc') === 'sysex' ? 'SysEx messages do not use MIDI channels' : ''}
          onchange={(e) => {
            const rawVal = (e.target as HTMLSelectElement).value;
            // 'global' means inherit from global_channel (store as undefined)
            // Any numeric value means explicit channel override
            updateMidiField('channel', rawVal === 'global' ? undefined : parseInt(rawVal));
          }}
        >
          {#each channelOptions as opt}
            <option value={opt.value}>{opt.label}</option>
          {/each}
        </select>
      </div>
    </div>

    <button class="remove-btn" type="button" onclick={onRemove} title="Remove command">×</button>
  </div>
{/if}

<style>
  .command-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    border-radius: 6px;
  }

  .command-number {
    font-weight: 700;
    font-size: 13px;
    color: var(--accent-primary);
    min-width: 24px;
    text-align: center;
    background: var(--accent-primary-dim);
    border-radius: 4px;
    padding: 4px 0;
  }

  .command-fields {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 2fr 2fr 3fr;
    gap: 8px;
    align-items: start;
  }

  .field.sysex-data {
    grid-column: 2 / 4;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .field label {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1.2;
    display: block;
    min-height: 14px;
  }

  .field select,
  .field input {
    width: 100%;
    padding: 6px 10px;
    border: 1px solid var(--border-default);
    border-radius: 4px;
    font-size: 12px;
    line-height: 1.5;
    height: 30px;
    background: var(--bg-dark);
    color: var(--text-primary);
    transition: all 0.2s;
  }

  .field select:focus,
  .field input:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px var(--accent-primary-dim);
  }

  .remove-btn {
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 4px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 20px;
    line-height: 1;
    flex-shrink: 0;
    transition: background 0.2s;
  }

  .remove-btn:hover {
    background: #dc2626;
  }

  .sysex-input {
    font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
    font-size: 11px;
    letter-spacing: 0.5px;
  }

  .info-icon {
    display: inline-block;
    margin-left: 4px;
    color: var(--accent-primary);
    font-size: 12px;
    cursor: help;
    vertical-align: baseline;
    opacity: 0.8;
    transition: opacity 0.2s;
    position: relative;
    line-height: 1;
  }

  .info-icon:hover {
    opacity: 1;
  }

  /* Custom tooltip on hover */
  .info-icon[data-tooltip]:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    left: 50%;
    bottom: 100%;
    transform: translateX(-50%);
    margin-bottom: 8px;
    padding: 8px 12px;
    background: var(--bg-dark);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    font-size: 11px;
    line-height: 1.4;
    white-space: normal;
    width: 280px;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    z-index: 1000;
    pointer-events: none;
  }

  /* Tooltip arrow */
  .info-icon[data-tooltip]:hover::before {
    content: '';
    position: absolute;
    left: 50%;
    bottom: 100%;
    transform: translateX(-50%);
    margin-bottom: 2px;
    border: 6px solid transparent;
    border-top-color: var(--border-default);
    z-index: 1000;
    pointer-events: none;
  }

  .field select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
