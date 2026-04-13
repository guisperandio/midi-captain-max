//! Tauri commands for config file operations

use crate::config::MidiCaptainConfig;
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::time::Duration;
use tauri::command;

#[cfg(unix)]
use std::os::unix::fs::MetadataExt;

/// Known device volume names (for validation)
const DEVICE_VOLUMES: &[&str] = &["CIRCUITPY", "MIDICAPTAIN"];

/// Get volume name for a path (cross-platform)
#[cfg(target_os = "windows")]
fn get_path_volume_name(path: &Path) -> Option<String> {
    use std::ffi::OsString;
    use std::os::windows::ffi::OsStrExt;
    use std::os::windows::ffi::OsStringExt;

    // Get the root path (e.g., "C:\" from "C:\Users\...")
    let mut components = path.components();
    let root = components.next()?;
    let root_path = PathBuf::from(root.as_os_str());
    let root_str = format!("{}\\", root_path.display());

    let mut volume_name: Vec<u16> = vec![0; 261];

    unsafe {
        let root_wide: Vec<u16> = OsString::from(&root_str)
            .encode_wide()
            .chain(Some(0))
            .collect();

        let result = winapi::um::fileapi::GetVolumeInformationW(
            root_wide.as_ptr(),
            volume_name.as_mut_ptr(),
            volume_name.len() as winapi::shared::minwindef::DWORD,
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            std::ptr::null_mut(),
            0,
        );

        if result != 0 {
            let len = volume_name
                .iter()
                .position(|&c| c == 0)
                .unwrap_or(volume_name.len());
            let name = OsString::from_wide(&volume_name[..len]);
            return name.into_string().ok();
        }
    }

    None
}

#[cfg(not(target_os = "windows"))]
fn get_path_volume_name(path: &Path) -> Option<String> {
    // On Unix, find the volume under /Volumes/ or /media/
    for ancestor in path.ancestors() {
        if let Some(parent) = ancestor.parent() {
            let parent_str = parent.to_string_lossy();
            if parent_str == "/Volumes"
                || parent_str.starts_with("/media/")
                || parent_str.starts_with("/run/media/")
            {
                return ancestor.file_name()?.to_str().map(|s| s.to_string());
            }
        }
    }
    None
}

/// Error type for config operations
#[derive(Debug, serde::Serialize)]
pub struct ConfigError {
    pub message: String,
    pub details: Option<Vec<String>>,
}

impl From<std::io::Error> for ConfigError {
    fn from(e: std::io::Error) -> Self {
        ConfigError {
            message: e.to_string(),
            details: None,
        }
    }
}

impl From<serde_json::Error> for ConfigError {
    fn from(e: serde_json::Error) -> Self {
        ConfigError {
            message: format!("JSON parse error: {}", e),
            details: None,
        }
    }
}

/// Validate that a path is on a recognized MIDI Captain device volume.
/// Prevents path traversal attacks by ensuring paths are within expected directories.
///
/// Accepts:
/// 1. Volumes with a known name (CIRCUITPY or MIDICAPTAIN), or
/// 2. Volumes whose config.json identifies as MIDI Captain **and** whose
///    `usb_drive_name` matches the actual volume name (case-insensitive).
///    This limits the surface: an arbitrary volume won't pass validation
///    just because someone placed a config.json on it.
fn validate_device_path(path: &str) -> Result<PathBuf, ConfigError> {
    let path = Path::new(path);

    // Canonicalize to resolve any .. or symlinks
    let canonical = path.canonicalize().map_err(|e| ConfigError {
        message: format!("Input watch path is neither a file nor a directory: {}", e),
        details: None,
    })?;

    // Check if the path is on a valid device volume
    let volume_name = get_path_volume_name(&canonical).ok_or_else(|| ConfigError {
        message: "Could not determine volume name for path".to_string(),
        details: None,
    })?;

    // Accept well-known volume names
    if DEVICE_VOLUMES
        .iter()
        .any(|v| volume_name.eq_ignore_ascii_case(v))
    {
        return Ok(canonical);
    }

    // Accept volumes that contain a valid MIDI Captain config.json.
    // If usb_drive_name is explicitly declared in the config, it must match
    // the actual volume name — preventing a stray config.json on an unrelated
    // volume from passing. If usb_drive_name is not declared, require CircuitPython
    // marker file (boot_out.txt) to prove this is a real CircuitPython device.
    if let Some(volume_path) = get_volume_path(&canonical) {
        let config_path = volume_path.join("config.json");
        if crate::device::is_midi_captain_config(&config_path) {
            match crate::device::parse_midi_captain_config(&config_path) {
                Some(declared_name) if declared_name.eq_ignore_ascii_case(&volume_name) => {
                    return Ok(canonical);
                }
                None => {
                    // No custom name declared — require CircuitPython marker file
                    // boot_out.txt is created by CircuitPython on every boot
                    let boot_out = volume_path.join("boot_out.txt");
                    if boot_out.exists() {
                        return Ok(canonical);
                    }
                    // Fall through to error - no usb_drive_name and no CircuitPython marker
                }
                _ => {} // declared name doesn't match this volume
            }
        }
    }

    Err(ConfigError {
        message: format!(
            "Path must be on a MIDI Captain device (CIRCUITPY, MIDICAPTAIN, or a custom-named volume whose config.json usb_drive_name matches), found: {}",
            volume_name
        ),
        details: None,
    })
}

/// Check if a volume is still mounted (not being ejected)
/// Compares device ID of volume vs root - if same, volume is not a separate filesystem
#[cfg(not(target_os = "windows"))]
fn is_volume_mounted(volume_path: &Path) -> bool {
    #[cfg(unix)]
    {
        if let (Ok(vol_meta), Ok(root_meta)) = (volume_path.metadata(), Path::new("/").metadata()) {
            vol_meta.dev() != root_meta.dev()
        } else {
            false
        }
    }
    #[cfg(not(unix))]
    {
        // On non-Unix systems, just check if path exists
        volume_path.exists()
    }
}

/// Get the volume/drive root path from a file path
/// e.g., /Volumes/CIRCUITPY from /Volumes/CIRCUITPY/config.json on macOS
/// or C:\ from C:\config.json on Windows
#[cfg(target_os = "windows")]
fn get_volume_path(path: &Path) -> Option<PathBuf> {
    // On Windows, get the drive root (e.g., C:\)
    let mut components = path.components();
    components.next().map(|c| PathBuf::from(c.as_os_str()))
}

#[cfg(not(target_os = "windows"))]
fn get_volume_path(path: &Path) -> Option<PathBuf> {
    // On Unix, find the mount point under /Volumes/, /media/, or /run/media/
    path.ancestors()
        .find(|p| {
            if let Some(parent) = p.parent() {
                let parent_str = parent.to_string_lossy();
                parent_str == "/Volumes"
                    || parent_str.starts_with("/media/")
                    || parent_str.starts_with("/run/media/")
            } else {
                false
            }
        })
        .map(|p| p.to_path_buf())
}

/// Verify the device is still mounted before writing
#[cfg(target_os = "windows")]
fn verify_device_connected(path: &Path) -> Result<(), ConfigError> {
    // On Windows, verify the file path exists (parent must exist for new files)
    // The device scanner already filtered to safe drive types
    if !path.exists() {
        let parent = path.parent().unwrap_or(path);
        if !parent.exists() {
            return Err(ConfigError {
                message: format!("Device path does not exist: {}", path.display()),
                details: Some(vec!["Device may have been ejected or unmounted".to_string()]),
            });
        }
    }
    
    Ok(())
}

#[cfg(not(target_os = "windows"))]
fn verify_device_connected(path: &Path) -> Result<(), ConfigError> {
    if let Some(volume_path) = get_volume_path(path) {
        if !is_volume_mounted(&volume_path) {
            return Err(ConfigError {
                message: "Device was disconnected".to_string(),
                details: None,
            });
        }
    }
    Ok(())
}

/// Write data to a file and sync to physical storage before returning.
///
/// `fs::write` closes the file without an explicit fsync, leaving data in the
/// OS page cache. On a USB-connected FAT32 device (CircuitPython), a power
/// cycle immediately after save can race the flush and the device boots with
/// stale data. Keeping the write handle open for `sync_all` before drop
/// ensures the data reaches the device's flash.
fn write_sync(path: &Path, data: &[u8]) -> Result<(), std::io::Error> {
    let mut file = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(path)?;
    file.write_all(data)?;
    file.sync_all()?;
    Ok(())
}

/// Read config from a file path
#[command]
pub fn read_config(path: String) -> Result<MidiCaptainConfig, ConfigError> {
    tracing::debug!(path = %path, "Reading config");
    let canonical = validate_device_path(&path).map_err(|e| {
        tracing::error!(path = %path, error = %e.message, "Failed to validate device path");
        e
    })?;
    let contents = fs::read_to_string(&canonical).map_err(|e| {
        tracing::error!(canonical = %canonical.display(), error = %e, "Failed to read config file");
        ConfigError::from(e)
    })?;
    let config: MidiCaptainConfig = serde_json::from_str(&contents).map_err(|e| {
        tracing::error!(canonical = %canonical.display(), error = %e, "Failed to parse config JSON");
        ConfigError::from(e)
    })?;
    tracing::info!(path = %path, device = ?config.device, "Config loaded successfully");
    Ok(config)
}

/// Read raw JSON from a file (for text editor)
#[command]
pub fn read_config_raw(path: String) -> Result<String, ConfigError> {
    let canonical = validate_device_path(&path)?;
    let contents = fs::read_to_string(&canonical)?;
    // Pretty-print the JSON
    let value: serde_json::Value = serde_json::from_str(&contents)?;
    let pretty = serde_json::to_string_pretty(&value)?;
    Ok(pretty)
}

/// Write config to a file path
#[command]
pub fn write_config(path: String, config: MidiCaptainConfig) -> Result<(), ConfigError> {
    tracing::debug!(path = %path, device = ?config.device, "Writing config");
    let canonical = validate_device_path(&path).map_err(|e| {
        tracing::error!(path = %path, error = %e.message, "Failed to validate device path");
        e
    })?;

    // Verify volume is still mounted
    verify_device_connected(&canonical).map_err(|e| {
        tracing::error!(canonical = %canonical.display(), error = %e.message, "Device disconnected");
        e
    })?;

    // Validate before writing
    if let Err(errors) = config.validate() {
        tracing::error!(canonical = %canonical.display(), errors = ?errors, "Config validation failed");
        return Err(ConfigError {
            message: "Validation failed".to_string(),
            details: Some(errors),
        });
    }

    let json = serde_json::to_string_pretty(&config).map_err(|e| {
        tracing::error!(canonical = %canonical.display(), error = %e, "Failed to serialize config");
        ConfigError::from(e)
    })?;
    
    write_sync(&canonical, json.as_bytes()).map_err(|e| {
        tracing::error!(canonical = %canonical.display(), error = %e, "Failed to write config file");
        e
    })?;

    tracing::info!(path = %path, "Config written successfully");
    Ok(())
}

/// Write raw JSON to a file (from text editor)
#[command]
pub fn write_config_raw(path: String, json: String) -> Result<(), ConfigError> {
    let canonical = validate_device_path(&path)?;

    // Verify volume is still mounted
    verify_device_connected(&canonical)?;

    // Validate JSON is parseable
    let config: MidiCaptainConfig = serde_json::from_str(&json)?;

    // Validate config
    if let Err(errors) = config.validate() {
        return Err(ConfigError {
            message: "Validation failed".to_string(),
            details: Some(errors),
        });
    }

    // Pretty-print and write
    let pretty = serde_json::to_string_pretty(&config)?;
    write_sync(&canonical, pretty.as_bytes())?;

    Ok(())
}

/// Validate JSON without writing
#[command]
pub fn validate_config(json: String) -> Result<(), ConfigError> {
    let config: MidiCaptainConfig = serde_json::from_str(&json)?;

    if let Err(errors) = config.validate() {
        return Err(ConfigError {
            message: "Validation failed".to_string(),
            details: Some(errors),
        });
    }

    Ok(())
}

/// Safely eject/unmount a device volume
#[command]
pub fn eject_device(path: String) -> Result<String, ConfigError> {
    tracing::info!(path = %path, "Ejecting device");
    
    // Validate path and get canonical path (avoids double canonicalization)
    let canonical = validate_device_path(&path).map_err(|e| {
        tracing::error!(path = %path, error = %e.message, "Failed to validate device path for eject");
        e
    })?;

    let volume_path = get_volume_path(&canonical).ok_or_else(|| {
        let err = ConfigError {
            message: "Could not determine volume path".to_string(),
            details: None,
        };
        tracing::error!(canonical = %canonical.display(), "Could not determine volume path");
        err
    })?;

    let volume_name = get_path_volume_name(&canonical).unwrap_or_else(|| "device".to_string());

    let volume_path_str = volume_path.to_string_lossy().to_string();

    #[cfg(target_os = "macos")]
    {
        let output = std::process::Command::new("diskutil")
            .args(["eject", &volume_path_str])
            .output()
            .map_err(|e| ConfigError {
                message: format!("Failed to eject device: {}", e),
                details: None,
            })?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(ConfigError {
                message: format!("Eject failed: {}", stderr),
                details: None,
            });
        }

        Ok(format!("Device '{}' ejected successfully", volume_name))
    }

    #[cfg(target_os = "linux")]
    {
        // Try gio first (modern GNOME/GTK)
        let gio_result = std::process::Command::new("gio")
            .args(&["mount", "-u", &volume_path_str])
            .output();

        if let Ok(output) = gio_result {
            if output.status.success() {
                return Ok(format!("Device '{}' ejected successfully", volume_name));
            }
        }

        // Fallback to umount
        let output = std::process::Command::new("umount")
            .arg(&volume_path_str)
            .output()
            .map_err(|e| ConfigError {
                message: format!("Failed to unmount device: {}", e),
                details: None,
            })?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(ConfigError {
                message: format!("Unmount failed: {}", stderr),
                details: None,
            });
        }

        Ok(format!("Device '{}' unmounted successfully", volume_name))
    }

    #[cfg(target_os = "windows")]
    {
        // Use PowerShell Shell.Application COM object for safe USB eject
        // Get drive letter (e.g., "E:"), handling both normal and verbatim paths
        let drive = match volume_path.components().next() {
            Some(std::path::Component::Prefix(prefix_component)) => match prefix_component.kind() {
                std::path::Prefix::Disk(letter)
                | std::path::Prefix::VerbatimDisk(letter) => {
                    format!("{}:", char::from(letter))
                }
                _ => {
                    return Err(ConfigError {
                        message: "Could not determine drive letter".to_string(),
                        details: None,
                    });
                }
            },
            _ => {
                return Err(ConfigError {
                    message: "Could not determine drive letter".to_string(),
                    details: None,
                });
            }
        };

        let script = format!(
            "(New-Object -ComObject Shell.Application).Namespace(17).ParseName('{}').InvokeVerb('Eject')",
            drive
        );

        let output = std::process::Command::new("powershell")
            .args(["-NoProfile", "-Command", &script])
            .output()
            .map_err(|e| ConfigError {
                message: format!("Failed to run PowerShell eject: {}", e),
                details: None,
            })?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(ConfigError {
                message: format!("Eject failed: {}. You can manually eject using 'Safely Remove Hardware' in the system tray.", stderr.trim()),
                details: None,
            });
        }

        Ok(format!("Device '{}' ejected successfully", volume_name))
    }
}

// ---------------------------------------------------------------------------
// Device auto-reload via serial
// ---------------------------------------------------------------------------

/// USB Vendor IDs for CircuitPython devices
const ADAFRUIT_VID: u16 = 0x239A;  // Adafruit boards
const RASPBERRY_PI_VID: u16 = 0x2E8A;  // RP2040/Pico boards

/// Find a CircuitPython serial port by looking for known CircuitPython VIDs.
/// On macOS each USB serial device may appear as both `/dev/cu.*` and `/dev/tty.*`.
/// When both are present, prefer `cu.*` (it doesn't block on open).
fn find_device_serial_port(_device_path: &Path) -> Result<String, ConfigError> {
    let ports = serialport::available_ports().map_err(|e| ConfigError {
        message: format!("Failed to enumerate serial ports: {}", e),
        details: None,
    })?;

    // Filter to known CircuitPython VID ports, preferring cu.* over tty.* on macOS
    let mut circuitpython_ports: Vec<_> = ports
        .iter()
        .filter(|p| {
            matches!(
                &p.port_type,
                serialport::SerialPortType::UsbPort(info) 
                    if info.vid == ADAFRUIT_VID || info.vid == RASPBERRY_PI_VID
            )
        })
        .collect();

    // On macOS, cu.* and tty.* are the same physical device — deduplicate.
    // Keep cu.* (call-up port, doesn't block waiting for carrier detect).
    if circuitpython_ports.len() > 1 {
        let has_cu = circuitpython_ports.iter().any(|p| p.port_name.contains("/cu."));
        if has_cu {
            circuitpython_ports.retain(|p| p.port_name.contains("/cu."));
        }
    }

    match circuitpython_ports.len() {
        0 => {
            // No VID-matched ports found. Try fallback heuristics based on port name.
            // This handles platforms/drivers where USB VID info isn't available.
            let fallback_ports: Vec<_> = ports
                .iter()
                .filter(|p| {
                    let name = p.port_name.to_lowercase();
                    name.contains("usbmodem") || name.contains("ttyacm") || name.starts_with("com")
                })
                .collect();
            
            match fallback_ports.len() {
                0 => Err(ConfigError {
                    message: "No CircuitPython serial port found. Is the device connected?".to_string(),
                    details: Some(vec!["Neither USB VID-matched ports nor fallback port names (usbmodem/ttyACM/COM) were found.".to_string()]),
                }),
                1 => Ok(fallback_ports[0].port_name.clone()),
                _ => {
                    // Multiple candidates, prefer cu.* on macOS if available
                    let mut candidates = fallback_ports;
                    let has_cu = candidates.iter().any(|p| p.port_name.contains("/cu."));
                    if has_cu {
                        candidates.retain(|p| p.port_name.contains("/cu."));
                    }
                    if candidates.len() == 1 {
                        Ok(candidates[0].port_name.clone())
                    } else {
                        Err(ConfigError {
                            message: format!("Found {} potential CircuitPython ports. Disconnect other devices and try again.", candidates.len()),
                            details: None,
                        })
                    }
                }
            }
        },
        1 => Ok(circuitpython_ports[0].port_name.clone()),
        _ => {
            // Multiple distinct CircuitPython devices.
            // Future: correlate by USB serial number.
            Err(ConfigError {
                message: format!(
                    "Found {} CircuitPython devices. Disconnect other devices and try again.",
                    circuitpython_ports.len()
                ),
                details: None,
            })
        }
    }
}

/// Soft-reboot a CircuitPython device by sending Ctrl-C + Ctrl-D over serial.
///
/// Ctrl-C (0x03) interrupts the running program and drops to REPL.
/// After 500ms delay for REPL initialization, Ctrl-D (0x04) triggers a soft reload
/// that re-reads config.json and restarts code.py. The USB drive stays mounted
/// throughout — no eject or power cycle needed.
///
/// Windows reliability improvements: Buffer draining and extended delays ensure
/// reliable reboot on Windows systems.
///
/// Future improvement: correlate device_path with USB serial port metadata
/// (serial number, bus location) to target the specific device that was just saved.
#[command]
pub fn trigger_device_reload(device_path: String) -> Result<String, ConfigError> {
    let canonical_path = validate_device_path(&device_path)?;
    verify_device_connected(&canonical_path)?;

    let serial_port = find_device_serial_port(&canonical_path)?;

    let mut port = serialport::new(&serial_port, 115200)
        .timeout(Duration::from_secs(2))
        .open()
        .map_err(|e| ConfigError {
            message: format!("Failed to open serial port {}: {}", serial_port, e),
            details: None,
        })?;

    // Ctrl-C: interrupt running program, drop to REPL
    // Send twice for Windows reliability
    port.write_all(&[0x03, 0x03]).map_err(|e| ConfigError {
        message: format!("Failed to send interrupt: {}", e),
        details: None,
    })?;

    port.flush().map_err(|e| ConfigError {
        message: format!("Failed to flush after Ctrl-C: {}", e),
        details: None,
    })?;

    // Wait for CircuitPython to stop the program and initialize the REPL
    std::thread::sleep(Duration::from_millis(500));

    // Drain any output from the interrupted program or REPL prompt
    // Loop until timeout to ensure buffer is fully drained
    // Add hard cap to prevent hanging if device produces continuous output
    port.set_timeout(Duration::from_millis(100)).map_err(|e| ConfigError {
        message: format!("Failed to set drain timeout: {}", e),
        details: None,
    })?;
    let mut drain_buf = [0u8; 256];
    let max_drain_iterations = 50;  // Max 5s drain time, 12.8KB data
    let mut iterations = 0;
    loop {
        if iterations >= max_drain_iterations {
            break;  // Hard cap to prevent hanging on continuous output
        }
        match port.read(&mut drain_buf) {
            Ok(0) => break,  // No data available
            Ok(_) => {
                iterations += 1;
                continue;  // Got data, keep draining
            }
            Err(ref e) if e.kind() == std::io::ErrorKind::TimedOut => break,  // Timeout means buffer is drained
            Err(_) => break,  // Other errors, stop draining
        }
    }
    
    // Restore original timeout for subsequent operations
    port.set_timeout(Duration::from_secs(2)).map_err(|e| ConfigError {
        message: format!("Failed to restore timeout: {}", e),
        details: None,
    })?;

    // Ctrl-D: soft reload — restarts code.py with new config
    // Send twice for Windows reliability
    port.write_all(&[0x04, 0x04]).map_err(|e| ConfigError {
        message: format!("Failed to send reload: {}", e),
        details: None,
    })?;

    port.flush().map_err(|e| ConfigError {
        message: format!("Failed to flush serial port: {}", e),
        details: None,
    })?;

    // Brief pause before closing so the bytes are fully transmitted
    std::thread::sleep(Duration::from_millis(100));

    Ok(format!("Device restarted via {}", serial_port))
}

// -----------------------------
// MIDI command wrappers (Tauri)
// -----------------------------

#[command]
pub fn list_midi_ports_cmd() -> Result<Vec<String>, ConfigError> {
    match crate::midi::list_midi_ports() {
        Ok(v) => Ok(v),
        Err(e) => Err(ConfigError {
            message: format!("MIDI error: {}", e),
            details: None,
        }),
    }
}

#[command]
pub fn send_midi_message_cmd(port_name: String, data: Vec<u8>) -> Result<(), ConfigError> {
    match crate::midi::send_midi_message(&port_name, data) {
        Ok(_) => Ok(()),
        Err(e) => Err(ConfigError {
            message: format!("MIDI send error: {}", e),
            details: None,
        }),
    }
}

#[command]
pub fn start_midi_input_listener_cmd(app: tauri::AppHandle, port_name: String) -> Result<(), ConfigError> {
    match crate::midi::start_midi_input_listener(app, port_name) {
        Ok(_) => Ok(()),
        Err(e) => Err(ConfigError {
            message: format!("MIDI listen error: {}", e),
            details: None,
        }),
    }
}

#[command]
pub fn stop_midi_input_listener_cmd() {
    crate::midi::stop_midi_input_listener();
}
