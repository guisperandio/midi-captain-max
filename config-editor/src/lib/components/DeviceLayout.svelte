<script lang="ts">
  import { config, getButtonErrors } from '$lib/formStore';
  import { selectedButtonIndex } from '$lib/stores';
  import { BUTTON_COLORS } from '$lib/types';
  import type { ButtonConfig } from '$lib/types';

  let buttons = $derived($config.buttons);
  let deviceType = $derived($config.device ?? 'std10');
  let totalSlots = $derived(deviceType === 'mini6' ? 6 : 10);
  let deviceName = $derived(deviceType === 'mini6' ? 'MINI 6' : 'CAPTAIN 10');

  // SVG dimensions based on device type - increased for header/footer
  let viewBox = $derived(deviceType === 'mini6' ? '0 0 560 600' : '0 0 900 650');
  let maxWidth = $derived(deviceType === 'mini6' ? 560 : 900);
  let cols = $derived(deviceType === 'mini6' ? 3 : 5);

  // Button layout constants
  const BUTTON_SIZE = 120;
  const BUTTON_SPACING = 40;
  const BUTTON_RADIUS = 12;
  const LED_RING_RADIUS = 65; // Radius for LED ring around button
  const LED_RING_WIDTH = 4; // Thickness of LED ring
  const HEADER_HEIGHT = 80;
  const FOOTER_HEIGHT = 60;

  // Calculate button position (accounting for header)
  function getButtonPosition(index: number): { x: number; y: number } {
    const row = Math.floor(index / cols);
    const col = index % cols;
    return {
      x: BUTTON_SPACING + col * (BUTTON_SIZE + BUTTON_SPACING),
      y: HEADER_HEIGHT + 40 + row * (BUTTON_SIZE + BUTTON_SPACING + 40)
    };
  }

  // Get button config safely
  function getButton(index: number): ButtonConfig | null {
    return buttons[index] ?? null;
  }

  // Get LED color for button
  function getLedColor(btn: ButtonConfig | null): string {
    if (!btn) return '#6b7280'; // Gray for empty
    return BUTTON_COLORS[btn.color] ?? '#ffffff';
  }

  // Get button label
  function getButtonLabel(btn: ButtonConfig | null, index: number): string {
    if (!btn) return `${index + 1}`;
    const label = btn.label || `${index + 1}`;
    // Truncate to 6 chars with ellipsis
    return label.length > 6 ? label.slice(0, 5) + '…' : label;
  }

  // Check if button has validation errors
  function hasButtonErrors(index: number): boolean {
    const errors = getButtonErrors(index);
    return errors.size > 0;
  }

  // Get button mode display
  function getButtonMode(btn: ButtonConfig | null): string {
    if (!btn) return '';
    const mode = btn.mode || 'toggle';
    switch (mode) {
      case 'normal': return 'N';
      case 'toggle': return 'T';
      case 'momentary': return 'M';
      case 'select': return 'S';
      case 'tap': return 'TAP';
      default: return 'T';
    }
  }

  // Get mode badge color
  function getModeBadgeColor(btn: ButtonConfig | null): string {
    if (!btn) return '#6b7280';
    const mode = btn.mode || 'toggle';
    switch (mode) {
      case 'normal': return '#6b7280'; // gray
      case 'toggle': return '#3b82f6'; // blue
      case 'momentary': return '#10b981'; // green
      case 'select': return '#f59e0b'; // amber
      case 'tap': return '#ec4899'; // pink
      default: return '#6b7280';
    }
  }

  // Check if button has multiple commands
  function isMultiCommand(btn: ButtonConfig | null): boolean {
    if (!btn) return false;
    const keytimes = btn.keytimes ?? 1;
    if (keytimes > 1) return true;
    return (btn.press?.length ?? 0) > 1 ||
           (btn.release?.length ?? 0) > 0 ||
           (btn.long_press?.length ?? 0) > 0 ||
           (btn.long_release?.length ?? 0) > 0;
  }

  // Get command count for badge
  function getCommandCount(btn: ButtonConfig | null): number {
    if (!btn) return 0;
    return (btn.press?.length ?? 0) +
           (btn.release?.length ?? 0) +
           (btn.long_press?.length ?? 0) +
           (btn.long_release?.length ?? 0);
  }

  // Get tooltip text
  function getTooltip(btn: ButtonConfig | null, index: number): string {
    if (!btn) return `Button ${index + 1} (not configured)`;

    const keytimes = btn.keytimes ?? 1;

    // For multi-state buttons
    if (keytimes > 1 && btn.states) {
      const lines: string[] = [`Button ${index + 1}: ${getButtonLabel(btn, index)}`, `${keytimes} States:`];
      btn.states.forEach((state, i) => {
        const stateLabel = state.label || `State ${i + 1}`;
        const stateColor = state.color || btn.color;
        lines.push(`${stateLabel} (${stateColor})`);
      });
      return lines.join('\n');
    }

    const formatCmd = (c: any) => {
      const t = c.type ?? 'cc';
      const ch = c.channel !== undefined ? ` Ch${c.channel + 1}` : '';
      if (t === 'cc') return `CC${c.cc}=${c.value}${ch}`;
      if (t === 'note') return `Note${c.note} vel${c.velocity}${ch}`;
      if (t === 'pc') return `PC${c.program}${ch}`;
      if (t === 'pc_inc') return `PC+${c.pc_step ?? 1}${ch}`;
      if (t === 'pc_dec') return `PC-${c.pc_step ?? 1}${ch}`;
      return t;
    };

    const lines: string[] = [`Button ${index + 1}: ${getButtonLabel(btn, index)}`];
    if (btn.press?.length) {
      lines.push(`Press: ${btn.press.map(formatCmd).join(', ')}`);
    }
    if (btn.release?.length) {
      lines.push(`Release: ${btn.release.map(formatCmd).join(', ')}`);
    }
    if (btn.long_press?.length) {
      lines.push(`Long: ${btn.long_press.map(formatCmd).join(', ')}`);
    }
    if (btn.long_release?.length) {
      lines.push(`Long Release: ${btn.long_release.map(formatCmd).join(', ')}`);
    }
    return lines.join('\n');
  }

  // Handle button click
  function handleButtonClick(index: number) {
    $selectedButtonIndex = index;
  }

  // Check if button is selected
  function isSelected(index: number): boolean {
    return $selectedButtonIndex === index;
  }
</script>

<div class="device-layout-container">
  <svg {viewBox} class="device-svg" style="max-width: {maxWidth}px;">
    <!-- Device Background with gradient -->
    <defs>
      <linearGradient id="deviceBg" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
        <stop offset="100%" style="stop-color:#0a0a0a;stop-opacity:1" />
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
      <filter id="buttonShadow">
        <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.5"/>
      </filter>
    </defs>

    <!-- Device Background Panel -->
    <rect width="100%" height="100%" fill="url(#deviceBg)" rx="8" />

    <!-- Device Header -->
    <g class="device-header">
      <!-- Header Background -->
      <rect x="0" y="0" width="100%" height="{HEADER_HEIGHT}" fill="#1a1a1a" />
      
      <!-- MIDI CAPTAIN Branding -->
      <text
        x="50%"
        y="30"
        class="brand-text"
        text-anchor="middle"
        dominant-baseline="middle"
      >
        MIDI CAPTAIN
      </text>
      
      <!-- Device Name -->
      <text
        x="50%"
        y="55"
        class="device-name-text"
        text-anchor="middle"
        dominant-baseline="middle"
      >
        {deviceName}
      </text>
    </g>

    <!-- Port Labels (top edge) -->
    {#if deviceType === 'std10'}
      <g class="port-labels">
        <text x="40" y="{HEADER_HEIGHT + 20}" class="port-label">USB</text>
        <text x="140" y="{HEADER_HEIGHT + 20}" class="port-label">DC 9V</text>
        <text x="260" y="{HEADER_HEIGHT + 20}" class="port-label">MIDI OUT</text>
        <text x="380" y="{HEADER_HEIGHT + 20}" class="port-label">MIDI IN</text>
        <text x="500" y="{HEADER_HEIGHT + 20}" class="port-label">EXP 1</text>
        <text x="600" y="{HEADER_HEIGHT + 20}" class="port-label">EXP 2</text>
      </g>
    {:else}
      <g class="port-labels">
        <text x="60" y="{HEADER_HEIGHT + 20}" class="port-label">USB</text>
        <text x="180" y="{HEADER_HEIGHT + 20}" class="port-label">DC 9V</text>
        <text x="300" y="{HEADER_HEIGHT + 20}" class="port-label">MIDI OUT</text>
        <text x="420" y="{HEADER_HEIGHT + 20}" class="port-label">MIDI IN</text>
      </g>
    {/if}

    <!-- Buttons with LED Rings -->
    {#each Array(totalSlots) as _, index}
      {@const pos = getButtonPosition(index)}
      {@const btn = getButton(index)}
      {@const ledColor = getLedColor(btn)}
      {@const label = getButtonLabel(btn, index)}
      {@const selected = isSelected(index)}
      {@const multiCmd = isMultiCommand(btn)}
      {@const cmdCount = getCommandCount(btn)}
      {@const tooltip = getTooltip(btn, index)}
      {@const mode = getButtonMode(btn)}
      {@const modeColor = getModeBadgeColor(btn)}
      {@const hasErrors = hasButtonErrors(index)}
      {@const centerX = pos.x + BUTTON_SIZE / 2}
      {@const centerY = pos.y + BUTTON_SIZE / 2}

      <!-- Button Group -->
      <g
        class="button-group"
        class:selected
        role="button"
        tabindex={0}
        aria-label="Button {index + 1}"
        aria-pressed={selected}
        onclick={() => handleButtonClick(index)}
        onkeydown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleButtonClick(index);
          }
        }}
      >
        <title>{tooltip}</title>

        <!-- LED Ring around button -->
        <circle
          cx={centerX}
          cy={centerY}
          r={LED_RING_RADIUS}
          class="led-ring"
          stroke={ledColor}
          stroke-width={LED_RING_WIDTH}
          fill="none"
          style="filter: drop-shadow(0 0 8px {ledColor}); opacity: 0.8;"
        />

        <!-- Button Rectangle with 3D effect -->
        <rect
          x={pos.x}
          y={pos.y}
          width={BUTTON_SIZE}
          height={BUTTON_SIZE}
          rx={BUTTON_RADIUS}
          ry={BUTTON_RADIUS}
          class="button-rect"
          class:selected
          class:multi-command={multiCmd}
          filter="url(#buttonShadow)"
        />

        <!-- Inner button highlight for 3D effect -->
        <rect
          x={pos.x + 4}
          y={pos.y + 4}
          width={BUTTON_SIZE - 8}
          height={BUTTON_SIZE - 8}
          rx={BUTTON_RADIUS - 2}
          ry={BUTTON_RADIUS - 2}
          class="button-highlight"
        />

        <!-- Button Label -->
        <text
          x={centerX}
          y={centerY}
          class="button-label"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {label}
        </text>

        <!-- Multi-command Badge (top-right) -->
        {#if multiCmd && cmdCount > 0}
          <g class="badge-group">
            <title>{tooltip}</title>
            <rect
              x={pos.x + BUTTON_SIZE - 35}
              y={pos.y + 5}
              width="30"
              height="20"
              rx="4"
              class="badge-bg"
            />
            <text
              x={pos.x + BUTTON_SIZE - 20}
              y={pos.y + 15}
              class="badge-text"
              text-anchor="middle"
              dominant-baseline="middle"
            >
              ×{cmdCount}
            </text>
          </g>
        {/if}

        <!-- Error Indicator (top-left) -->
        {#if hasErrors}
          <g class="error-indicator">
            <circle
              cx={pos.x + 15}
              cy={pos.y + 15}
              r="10"
              fill="#dc2626"
            />
            <text
              x={pos.x + 15}
              y={pos.y + 15}
              class="error-icon"
              text-anchor="middle"
              dominant-baseline="middle"
            >
              !
            </text>
          </g>
        {/if}

        <!-- Mode Badge (bottom-left) -->
        {#if mode}
          <g class="mode-badge-group">
            <rect
              x={pos.x + 5}
              y={pos.y + BUTTON_SIZE - 25}
              width={mode === 'TAP' ? 35 : 24}
              height="20"
              rx="4"
              class="mode-badge-bg"
              fill={modeColor}
            />
            <text
              x={pos.x + (mode === 'TAP' ? 22.5 : 17)}
              y={pos.y + BUTTON_SIZE - 15}
              class="mode-badge-text"
              text-anchor="middle"
              dominant-baseline="middle"
            >
              {mode}
            </text>
          </g>
        {/if}
      </g>
    {/each}

    <!-- Encoder and Expression Indicators (between rows for STD10) -->
    {#if deviceType === 'std10'}
      {@const midY = HEADER_HEIGHT + 40 + BUTTON_SIZE + 20}
      {@const encoderX = maxWidth / 2 - 60}
      {@const exp1X = maxWidth / 2 + 40}
      
      <!-- Encoder -->
      <g class="control-indicator">
        <circle cx={encoderX} cy={midY} r="20" class="encoder-circle" />
        <circle cx={encoderX} cy={midY} r="12" class="encoder-inner" />
        <line x1={encoderX} y1={midY - 12} x2={encoderX} y2={midY - 8} class="encoder-marker" stroke="#8b5cf6" stroke-width="2" />
        <text x={encoderX} y={midY + 35} class="control-label" text-anchor="middle">ENCODER</text>
      </g>
      
      <!-- Expression Pedals -->
      <g class="control-indicator">
        <rect x={exp1X - 15} y={midY - 18} width="30" height="36" rx="3" class="exp-rect" />
        <line x1={exp1X - 10} y1={midY + 8} x2={exp1X + 10} y2={midY - 8} class="exp-line" stroke="#10b981" stroke-width="2" />
        <text x={exp1X} y={midY + 35} class="control-label" text-anchor="middle">EXP 1/2</text>
      </g>
    {:else}
      <!-- Mini6 - centered encoder indicator -->
      {@const midY = HEADER_HEIGHT + 40 + BUTTON_SIZE + 20}
      {@const encoderX = maxWidth / 2}
      
      <g class="control-indicator">
        <circle cx={encoderX} cy={midY} r="20" class="encoder-circle" />
        <circle cx={encoderX} cy={midY} r="12" class="encoder-inner" />
        <line x1={encoderX} y1={midY - 12} x2={encoderX} y2={midY - 8} class="encoder-marker" stroke="#8b5cf6" stroke-width="2" />
        <text x={encoderX} y={midY + 35} class="control-label" text-anchor="middle">ENCODER</text>
      </g>
    {/if}
  </svg>
</div>

<style>
  .device-layout-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 24px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  }

  .device-svg {
    width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  }

  /* Device Header Styles */
  .brand-text {
    fill: #8b5cf6;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    filter: url(#glow);
  }

  .device-name-text {
    fill: #e5e7eb;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  /* Port Labels */
  .port-label {
    fill: #6b7280;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Button Styles */
  .button-group {
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .button-group:hover .button-rect {
    fill: #2d3748;
  }

  .button-group:hover .led-ring {
    opacity: 1 !important;
    stroke-width: 5;
  }

  .button-group:focus {
    outline: none;
  }

  .button-group:focus .button-rect {
    stroke: #8b5cf6;
    stroke-width: 3;
  }

  .button-rect {
    fill: #1a202c;
    stroke: #2d3748;
    stroke-width: 2;
    transition: all 0.2s ease;
  }

  .button-rect.selected {
    fill: #2d1b4e;
    stroke: #8b5cf6;
    stroke-width: 3;
  }

  .button-highlight {
    fill: rgba(255, 255, 255, 0.05);
    pointer-events: none;
  }

  .button-group.selected .button-highlight {
    fill: rgba(139, 92, 246, 0.15);
  }

  .button-label {
    fill: #ffffff;
    font-size: 14px;
    font-weight: 600;
    pointer-events: none;
    user-select: none;
  }

  /* LED Ring Styles */
  .led-ring {
    transition: all 0.3s ease;
    stroke-linecap: round;
  }

  .button-group.selected .led-ring {
    stroke-width: 6;
    opacity: 1 !important;
  }

  /* Badge Styles */
  .badge-group {
    pointer-events: none;
  }

  .badge-bg {
    fill: #8b5cf6;
  }

  .badge-text {
    fill: #ffffff;
    font-size: 11px;
    font-weight: 700;
  }

  .mode-badge-group {
    pointer-events: none;
  }

  .mode-badge-bg {
    opacity: 0.9;
  }

  .mode-badge-text {
    fill: #ffffff;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .error-indicator {
    pointer-events: none;
  }

  .error-icon {
    fill: #ffffff;
    font-size: 14px;
    font-weight: 900;
  }

  /* Control Indicators (Encoder, Expression) */
  .control-indicator {
    opacity: 0.6;
  }

  .encoder-circle {
    fill: #1a202c;
    stroke: #4a5568;
    stroke-width: 2;
  }

  .encoder-inner {
    fill: #2d3748;
    stroke: #8b5cf6;
    stroke-width: 1;
  }

  .encoder-marker {
    stroke-linecap: round;
  }

  .exp-rect {
    fill: #1a202c;
    stroke: #4a5568;
    stroke-width: 2;
  }

  .exp-line {
    stroke-linecap: round;
  }

  .control-label {
    fill: #6b7280;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  /* Keyboard accessibility */
  .button-group:focus-visible .button-rect {
    stroke: #8b5cf6;
    stroke-width: 3;
    outline: 2px solid #8b5cf6;
    outline-offset: 2px;
  }
</style>
