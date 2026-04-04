<script lang="ts">
  interface Props {
    checked?: boolean;
    disabled?: boolean;
    label?: string;
    onchange?: (checked: boolean) => void;
  }

  let {
    checked = $bindable(false),
    disabled = false,
    label = '',
    onchange
  }: Props = $props();

  function handleChange(e: Event) {
    if (disabled) return;
    const target = e.target as HTMLInputElement;
    checked = target.checked;
    onchange?.(checked);
  }
</script>

<label class="toggle-container" class:disabled>
  {#if label}
    <span class="toggle-header">{label}</span>
  {/if}
  <div class="toggle-control">
    <span class="toggle-wrapper">
      <input
        type="checkbox"
        bind:checked
        {disabled}
        class="toggle-input"
        onchange={handleChange}
      />
      <div
        class="toggle-track"
        class:checked
        role="presentation"
      >
        <div class="toggle-thumb" class:checked></div>
      </div>
    </span>
    <div class="toggle-states">
      <span class="state-label" class:active={checked}>On</span>
      <span class="state-label" class:active={!checked}>Off</span>
    </div>
  </div>
</label>

<style>
  .toggle-container {
    display: inline-flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    cursor: pointer;
    user-select: none;
  }

  .toggle-container.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .toggle-header {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }

  .toggle-control {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .toggle-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .toggle-input {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }

  .toggle-track {
    position: relative;
    width: 32px;
    height: 56px;
    background: #1a1a1a;
    border: 2px solid #333333;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .toggle-track:hover:not(.disabled):not(.checked) {
    border-color: #444444;
    background: #222222;
  }

  .toggle-track.checked {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    box-shadow: 0 0 8px rgba(0, 212, 170, 0.3);
  }

  .toggle-track.checked:hover:not(.disabled) {
    background: #00d4b4;
    border-color: #00d4b4;
    box-shadow: 0 0 12px rgba(0, 212, 170, 0.4);
  }

  .toggle-input:focus-visible + .toggle-track {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.1);
  }

  .toggle-thumb {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 24px;
    height: 24px;
    background: #666666;
    border-radius: 50%;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    transform: translateY(26px); /* Start at bottom (OFF position) */
  }

  .toggle-thumb.checked {
    transform: translateY(0); /* Move to top (ON position) */
    background: #0a0a0a;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  }

  .toggle-states {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .state-label {
    font-size: 13px;
    color: #4b5563;
    font-weight: 500;
    transition: color 0.2s ease;
  }

  .state-label.active {
    color: #e5e7eb;
  }

  .disabled .toggle-track,
  .disabled .toggle-thumb {
    cursor: not-allowed;
  }
</style>
