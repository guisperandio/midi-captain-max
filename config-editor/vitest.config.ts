import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'happy-dom',
		globals: false,  // Require explicit imports to avoid test pollution
		setupFiles: ['./vitest.setup.ts'],
		coverage: {
			reporter: ['text', 'json', 'html'],
			include: ['src/lib/**/*.ts', 'src/lib/**/*.svelte'],
			exclude: [
				'src/lib/bindings/**',  // Generated files
				'**/*.d.ts',
				'**/*.config.*',
				'**/*.test.*',
				'**/*.spec.*'
			]
			// Note: Global thresholds removed - will add per-file thresholds as modules gain test coverage
			// Current coverage: validation.ts (~47%), formStore.ts (~35%)
		}
	}
});
