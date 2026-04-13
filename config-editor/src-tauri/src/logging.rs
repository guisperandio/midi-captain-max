//! Logging infrastructure for MIDI Captain MAX Config Editor
//!
//! Logs are written to platform-specific locations:
//! - macOS: ~/Library/Logs/midi-captain-max-config-editor/
//! - Windows: %APPDATA%\midi-captain-max-config-editor\logs\
//! - Linux: ~/.local/share/midi-captain-max-config-editor/logs/

use std::path::PathBuf;
use tracing_subscriber::{fmt, layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

/// Get the log directory path for the current platform
pub fn get_log_dir() -> PathBuf {
    let app_name = "midi-captain-max-config-editor";
    
    #[cfg(target_os = "macos")]
    {
        if let Some(home) = dirs::home_dir() {
            return home.join("Library").join("Logs").join(app_name);
        }
    }
    
    #[cfg(target_os = "windows")]
    {
        if let Some(appdata) = std::env::var_os("APPDATA") {
            return PathBuf::from(appdata).join(app_name).join("logs");
        }
    }
    
    #[cfg(target_os = "linux")]
    {
        if let Some(data_dir) = dirs::data_local_dir() {
            return data_dir.join(app_name).join("logs");
        }
    }
    
    // Fallback to current directory
    PathBuf::from("logs")
}

/// Initialize the logging system
///
/// Sets up:
/// - Daily log file rotation (creates files like app.log.YYYY-MM-DD)
/// - Console output (in debug builds only)
/// - Compact text format with timestamps, module names, and line numbers
pub fn init() -> Result<PathBuf, Box<dyn std::error::Error>> {
    let log_dir = get_log_dir();
    
    // Create log directory if it doesn't exist
    std::fs::create_dir_all(&log_dir)?;
    
    // File appender with daily rotation
    let file_appender = tracing_appender::rolling::daily(&log_dir, "app.log");
    
    // Environment filter: default to INFO, allow override via RUST_LOG env var
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));
    
    // File layer - compact format with timestamps
    let file_layer = fmt::layer()
        .with_writer(file_appender)
        .with_ansi(false) // No color codes in files
        .with_target(true) // Include module names
        .with_line_number(true) // Include line numbers for errors
        .compact(); // Compact format (one line per log)
    
    #[cfg(debug_assertions)]
    {
        // Console layer - human-readable output for development
        let console_layer = fmt::layer()
            .with_writer(std::io::stderr)
            .pretty();
        
        tracing_subscriber::registry()
            .with(env_filter)
            .with(file_layer)
            .with(console_layer)
            .init();
    }
    
    #[cfg(not(debug_assertions))]
    {
        // Production: file only
        tracing_subscriber::registry()
            .with(env_filter)
            .with(file_layer)
            .init();
    }
    
    tracing::info!("Logging initialized");
    tracing::info!("Log directory: {}", log_dir.display());
    tracing::info!("Version: {}", env!("CARGO_PKG_VERSION"));
    tracing::info!("Build: {} {}", 
        std::env::consts::OS, 
        std::env::consts::ARCH
    );
    
    Ok(log_dir)
}

/// Tauri command to get log directory path
#[tauri::command]
pub fn get_log_path() -> String {
    get_log_dir().display().to_string()
}

/// Tauri command to read recent log entries
///
/// Daily rotation creates files like `app.log.2026-04-13`. This finds the newest
/// log file and reads the last N lines efficiently using a tail-like approach.
#[tauri::command]
pub fn get_recent_logs(lines: Option<usize>) -> Result<Vec<String>, String> {
    use std::fs;
    use std::io::{BufRead, BufReader};

    let log_dir = get_log_dir();
    
    // Find the newest app.log.* file (daily rotation creates dated files)
    let mut log_files: Vec<_> = fs::read_dir(&log_dir)
        .map_err(|e| format!("Failed to read log directory: {}", e))?
        .filter_map(|entry| entry.ok())
        .filter(|entry| {
            entry.file_name()
                .to_string_lossy()
                .starts_with("app.log")
        })
        .collect();
    
    if log_files.is_empty() {
        return Ok(vec!["No logs found".to_string()]);
    }
    
    // Sort by modification time, newest first
    log_files.sort_by_key(|entry| {
        entry.metadata()
            .and_then(|m| m.modified())
            .ok()
    });
    log_files.reverse();
    
    let log_file = log_files[0].path();
    let line_count = lines.unwrap_or(100);
    
    // Read file efficiently: use a ring buffer to keep only last N lines
    let file = fs::File::open(&log_file)
        .map_err(|e| format!("Failed to open log file: {}", e))?;
    let reader = BufReader::new(file);
    
    let mut ring_buffer: Vec<String> = Vec::with_capacity(line_count);
    let mut index = 0;
    
    for line in reader.lines() {
        let line = line.map_err(|e| format!("Failed to read line: {}", e))?;
        if ring_buffer.len() < line_count {
            ring_buffer.push(line);
        } else {
            ring_buffer[index % line_count] = line;
            index += 1;
        }
    }
    
    // If we didn't fill the buffer, return as-is (already in order)
    if ring_buffer.len() < line_count {
        return Ok(ring_buffer);
    }
    
    // If we wrapped around, reorder to get chronological order
    let start = index % line_count;
    let mut result = Vec::with_capacity(line_count);
    result.extend_from_slice(&ring_buffer[start..]);
    result.extend_from_slice(&ring_buffer[..start]);
    
    Ok(result)
}
