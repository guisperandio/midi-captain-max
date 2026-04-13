mod commands;
mod midi;
mod config;
mod device;
mod logging;

use commands::*;
use device::{scan_devices, start_device_watcher, stop_device_watcher};
use logging::{get_log_path, get_recent_logs};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Initialize logging - errors are non-fatal, just log to stderr
    // On Windows release builds, also write to a debug file since stderr is invisible
    if let Err(e) = logging::init() {
        eprintln!("Failed to initialize logging: {}", e);
        
        // Try to write error to a visible location for Windows debugging
        #[cfg(target_os = "windows")]
        {
            if let Some(appdata) = std::env::var_os("APPDATA") {
                use std::io::Write;
                let error_path = std::path::PathBuf::from(appdata)
                    .join("midi-captain-max-config-editor")
                    .join("startup-error.txt");
                if let Ok(()) = std::fs::create_dir_all(error_path.parent().unwrap()) {
                    if let Ok(mut file) = std::fs::File::create(&error_path) {
                        let _ = writeln!(file, "Failed to initialize logging: {}", e);
                        let _ = writeln!(file, "Time: {:?}", std::time::SystemTime::now());
                    }
                }
            }
        }
    }
    
    tracing::info!("Starting MIDI Captain MAX Config Editor");
    
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            read_config,
            read_config_raw,
            write_config,
            write_config_raw,
            validate_config,
            eject_device,
            trigger_device_reload,
            list_midi_ports_cmd,
            send_midi_message_cmd,
            start_midi_input_listener_cmd,
            stop_midi_input_listener_cmd,

            scan_devices,
            start_device_watcher,
            stop_device_watcher,
            
            get_log_path,
            get_recent_logs
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
