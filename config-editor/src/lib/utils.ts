/**
 * UI utility functions
 */

import type { MidiCaptainConfig } from './types';

/**
 * Format a MIDI channel number for display, using custom label if available
 * @param channelNum - Channel number (0-15)
 * @param config - Optional config for accessing channel_labels
 * @returns Formatted string like "Quad Cortex (Ch1)" or "Channel 1"
 */
export function formatChannel(
  channelNum: number,
  config?: MidiCaptainConfig
): string {
  const displayNum = channelNum + 1; // 0-15 → 1-16 for display
  
  if (config?.channel_labels) {
    const label = config.channel_labels[String(channelNum)];
    if (label) {
      return `${label} (Ch${displayNum})`;
    }
  }
  
  return `Channel ${displayNum}`;
}

/**
 * Get short channel label (just the device name if available, otherwise "Ch1")
 * @param channelNum - Channel number (0-15)
 * @param config - Optional config for accessing channel_labels
 * @returns Short label like "Quad Cortex" or "Ch1"
 */
export function formatChannelShort(
  channelNum: number,
  config?: MidiCaptainConfig
): string {
  const displayNum = channelNum + 1;
  
  if (config?.channel_labels) {
    const label = config.channel_labels[String(channelNum)];
    if (label) {
      return label;
    }
  }
  
  return `Ch${displayNum}`;
}

/**
 * Get the label for a channel, or null if no label is set
 * @param channelNum - Channel number (0-15)
 * @param config - Optional config for accessing channel_labels
 * @returns Label string or null
 */
export function getChannelLabel(
  channelNum: number,
  config?: MidiCaptainConfig
): string | null {
  if (config?.channel_labels) {
    return config.channel_labels[String(channelNum)] ?? null;
  }
  return null;
}
