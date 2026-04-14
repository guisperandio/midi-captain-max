import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'happy-dom',
		globals: true,
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
		}
	}
});
