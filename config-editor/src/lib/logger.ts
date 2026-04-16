/**
 * Frontend logging utility with dev/prod mode support
 * 
 * Usage:
 *   import { logger } from '$lib/logger';
 *   logger.debug('[APP] Testing MIDI ports...');  // Only in dev
 *   logger.info('[SAVE] Config written');          // Only in dev
 *   logger.warn('[SAVE] Serial reload failed', e); // Always shown
 *   logger.error('[EXPORT] Error:', error);        // Always shown
 */

const isDev = import.meta.env.DEV;

export const logger = {
  /**
   * Debug messages - only shown in development
   */
  debug: (...args: any[]) => {
    if (isDev) {
      console.log(...args);
    }
  },

  /**
   * Info messages - only shown in development
   */
  info: (...args: any[]) => {
    if (isDev) {
      console.log(...args);
    }
  },

  /**
   * Warnings - always shown
   */
  warn: (...args: any[]) => {
    console.warn(...args);
  },

  /**
   * Errors - always shown
   */
  error: (...args: any[]) => {
    console.error(...args);
  },

  /**
   * Group logging for better organization in dev tools
   */
  group: (label: string, fn: () => void) => {
    if (isDev) {
      console.group(label);
      try {
        fn();
      } finally {
        console.groupEnd();
      }
    }
  }
};
