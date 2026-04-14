<script lang="ts">
  import { config, updateField } from '$lib/formStore';

  // Create reactive array of all 16 channels with their labels
  let channelLabels = $derived(
    Array.from({ length: 16 }, (_, i) => ({
      channel: i,
      label: $config.channel_labels?.[String(i)] ?? ''
    }))
  );

  function handleLabelChange(channelNum: number, value: string) {
    const trimmed = value.trim();
    const currentLabels = $config.channel_labels ?? {};
    
    if (trimmed === '') {
      // Remove label if empty
      const newLabels = { ...currentLabels };
      delete newLabels[String(channelNum)];
      
      // If no labels left, set to undefined (will be omitted from JSON)
      updateField('channel_labels', Object.keys(newLabels).length > 0 ? newLabels : undefined);
    } else {
      // Add or update label
      updateField('channel_labels', {
        ...currentLabels,
        [String(channelNum)]: trimmed
      });
    }
  }

  function handleClearAll() {
    updateField('channel_labels', undefined);
  }

  let hasAnyLabels = $derived(
    $config.channel_labels && Object.keys($config.channel_labels).length > 0
  );
</script>

<div class="channel-labels-section">
  <div class="section-header">
    <h3>MIDI Channel Labels</h3>
    {#if hasAnyLabels}
      <button type="button" class="clear-all-btn" onclick={handleClearAll}>
        Clear All
      </button>
    {/if}
  </div>
  
  <p class="section-description">
    Assign custom names to MIDI channels (e.g., "Quad Cortex", "Timespace Delay"). 
    These labels will appear throughout the editor instead of generic channel numbers.
  </p>

  <div class="channel-grid">
    {#each channelLabels as { channel, label }}
      <div class="channel-row">
        <label for="ch-{channel}" class="channel-number">Ch{channel + 1}</label>
        <input
          id="ch-{channel}"
          type="text"
          value={label}
          placeholder="Device name (optional)"
          maxlength="30"
          onblur={(e) => handleLabelChange(channel, e.currentTarget.value)}
        />
      </div>
    {/each}
  </div>
</div>

<style>
  .channel-labels-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border-default);
    border-radius: 10px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .clear-all-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
    color: var(--text-secondary);
    background: transparent;
    border: 1px solid var(--border-default);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .clear-all-btn:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .section-description {
    font-size: 0.8125rem;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.5;
  }

  .channel-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .channel-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .channel-number {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-secondary);
    min-width: 2.5rem;
    text-align: right;
  }

  input[type="text"] {
    flex: 1;
    padding: 0.5rem;
    font-size: 0.8125rem;
    color: var(--text-primary);
    background: var(--bg-input);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    transition: all 0.15s;
  }

  input[type="text"]:focus {
    outline: none;
    border-color: var(--accent-primary);
    background: var(--bg-input-focus);
  }

  input[type="text"]::placeholder {
    color: var(--text-muted);
  }
</style>
