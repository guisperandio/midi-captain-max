# MIDI Captain Config Editor

Desktop application for editing MIDI Captain foot controller configurations.

**Stack:** Tauri 2 + SvelteKit 5 + TypeScript + Rust

## Development Setup

### Prerequisites
- Node.js 20+
- Rust (latest stable)
- Platform-specific dependencies:
  - **macOS**: Xcode Command Line Tools
  - **Linux**: `libgtk-3-dev libwebkit2gtk-4.1-dev libasound2-dev`
  - **Windows**: WebView2 (usually pre-installed)

### Installation

```bash
npm install
cd src-tauri && cargo build
```

### Running in Development

```bash
npm run tauri dev
```

## TypeScript Bindings (Type Safety)

TypeScript types in `src/lib/bindings/` are **auto-generated** from Rust structs using [ts-rs](https://github.com/Aleph-Alpha/ts-rs).

### ⚠️ DO NOT EDIT GENERATED FILES MANUALLY

All `.ts` files in `src/lib/bindings/` are generated. Manual edits will be overwritten.

### Regenerating Bindings

When changing config types in `src-tauri/src/config/`:

1. **Run tests** (this triggers binding generation):
   ```bash
   cd src-tauri
   cargo test --lib
   ```

2. **Copy to frontend** (bindings are gitignored, CI regenerates them):
   ```bash
   cp -r bindings/* ../src/lib/bindings/
   ```

3. **Commit both changes together**:
   ```bash
   git add src-tauri/src/config/*.rs
   git add src/lib/bindings/*.ts  # Will be regenerated in CI
   git commit -m "feat: update config types"
   ```

### Why This Approach?

- **Single source of truth**: Rust structs define the schema
- **Type safety**: TypeScript types always match Rust validation
- **No drift**: CI regenerates and verifies bindings on every push
- **Prevents bugs**: Type mismatches caught at compile time

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test:watch

# Run with coverage
npm run test:coverage

# Run type checking
npm run check
```

### Test Structure

- `src/lib/**/*.test.ts` - Unit tests for stores, validation, utilities
- `src/lib/testUtils.ts` - Type-safe test fixtures (use these instead of `as` casts)
- Coverage thresholds enforced: 80% lines, 80% functions, 75% branches

### CI Pipeline

1. **Generate bindings** (from Rust)
2. **Run Rust tests** (backend validation)
3. **Run frontend tests** (TypeScript/Svelte)
4. **Type check** (SvelteKit)
5. **Build** (macOS, Windows, Linux)

## Building for Production

```bash
# Build Tauri app
npm run tauri build

# Output: src-tauri/target/release/bundle/
```

## Recommended IDE Setup

**VS Code** with extensions:
- [Svelte for VS Code](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode)
- [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode)
- [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)
- [Vitest](https://marketplace.visualstudio.com/items?itemName=ZixuanChen.vitest-explorer)
