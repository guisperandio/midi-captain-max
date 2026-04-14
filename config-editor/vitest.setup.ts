import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// Mock Tauri API for tests
global.window = Object.create(window);
const mockTauri = {
	invoke: vi.fn()
};
Object.defineProperty(window, '__TAURI__', {
	value: mockTauri,
	writable: true
});
