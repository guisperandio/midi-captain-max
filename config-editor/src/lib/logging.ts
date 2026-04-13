/**
 * Logging utilities for accessing backend logs
 */

import { invoke } from '@tauri-apps/api/core'

/**
 * Get the platform-specific log directory path
 */
export async function getLogPath(): Promise<string> {
  return invoke('get_log_path')
}

/**
 * Get recent log entries
 * @param lines Number of recent lines to retrieve (default: 100)
 */
export async function getRecentLogs(lines?: number): Promise<string[]> {
  return invoke('get_recent_logs', { lines })
}

/**
 * Open the log directory in the system file manager
 */
export async function openLogDirectory(): Promise<void> {
  const { open } = await import('@tauri-apps/plugin-opener')
  const logPath = await getLogPath()
  await open(logPath)
}
