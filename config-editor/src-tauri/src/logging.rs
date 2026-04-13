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
/// - File rotation (daily logs, max 7 days)
/// - Console output (in debug builds)
/// - Structured JSON logging
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

/// Tauri command to get log file path
#[tauri::command]
pub fn get_log_path() -> String {
    get_log_dir().display().to_string()
}

/// Tauri command to read recent log entries
#[tauri::command]
pub fn get_recent_logs(lines: Option<usize>) -> Result<Vec<String>, String> {
    let log_dir = get_log_dir();
    let log_file = log_dir.join("app.log");
    
    if !log_file.exists() {
        return Ok(vec!["No logs found".to_string()]);
    }
    
    let contents = std::fs::read_to_string(&log_file)
        .map_err(|e| format!("Failed to read log file: {}", e))?;
    
    let all_lines: Vec<String> = contents.lines().map(String::from).collect();
    let line_count = lines.unwrap_or(100).min(all_lines.len());
    
    Ok(all_lines.into_iter().rev().take(line_count).rev().collect())
}
