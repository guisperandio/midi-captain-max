//! MIDI Captain configuration data structures
//!
//! Configuration model definitions for buttons, encoders, expressions, and main config.

use super::types::*;
use serde::{Deserialize, Serialize};
use ts_rs::TS;

// Default value functions for serde
fn default_bank_switch_method() -> BankSwitchMethod {
    BankSwitchMethod::Button
}

/// Per-state overrides for keytimes cycling
#[derive(Debug, Clone, Serialize, Deserialize, Default, TS)]
#[ts(export)]
pub struct StateOverride {
    // Multi-command event arrays (per-state actions)
    // Now supports conditional commands in addition to regular MIDI commands
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub press: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub release: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub long_press: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub long_release: Option<Vec<CommandOrConditional>>,

    // Legacy single-type field overrides
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc_on: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc_off: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub note: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub velocity_on: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub velocity_off: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub program: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pc_step: Option<u8>,

    // Visual overrides
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub color: Option<ButtonColor>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub label: Option<String>,
}

/// MIDI command for multi-command event arrays
#[derive(Debug, Clone, Serialize, Deserialize, Default, TS)]
#[ts(export)]
pub struct MidiCommand {
    #[serde(rename = "type", default)]
    pub command_type: MessageType,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub channel: Option<u8>,
    // CC fields
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub cc: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub value: Option<u8>,
    // Note fields
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub note: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub velocity: Option<u8>,
    // PC fields
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub program: Option<u8>,
    // PC inc/dec fields
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub pc_step: Option<u8>,
    // Optional threshold for long-press (on first command only)
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub threshold_ms: Option<u32>,
}

/// Conditional command wrapper for if/then/else logic
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct ConditionalCommand {
    #[serde(rename = "type")]
    pub command_type: String, // Always "conditional"
    #[serde(rename = "if")]
    pub condition: Condition,
    pub then: Vec<CommandOrConditional>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(rename = "else")]
    pub else_branch: Option<Vec<CommandOrConditional>>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub then_label: Option<String>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub else_label: Option<String>,
}

/// Union type for command arrays - can be regular MIDI commands or conditional wrappers
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
#[serde(untagged)]
pub enum CommandOrConditional {
    Midi(MidiCommand),
    Conditional(ConditionalCommand),
}

impl Default for CommandOrConditional {
    fn default() -> Self {
        CommandOrConditional::Midi(MidiCommand::default())
    }
}


/// Helper type to deserialize either a single command object or an array
/// Supports backward compatibility with legacy configs that use single objects
/// Now supports both MidiCommand and ConditionalCommand
#[derive(Debug, Clone, Deserialize)]
#[serde(untagged)]
enum OneOrMany {
    One(CommandOrConditional),
    Many(Vec<CommandOrConditional>),
}

impl OneOrMany {
    fn into_vec(self) -> Vec<CommandOrConditional> {
        match self {
            OneOrMany::One(cmd) => vec![cmd],
            OneOrMany::Many(cmds) => cmds,
        }
    }
}

impl Serialize for OneOrMany {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        // Always serialize as array
        match self {
            OneOrMany::One(cmd) => vec![cmd.clone()].serialize(serializer),
            OneOrMany::Many(cmds) => cmds.serialize(serializer),
        }
    }
}

/// Custom deserializer for backward compatibility: accepts single object or array
fn deserialize_one_or_many<'de, D>(
    deserializer: D,
) -> Result<Option<Vec<CommandOrConditional>>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    Option::<OneOrMany>::deserialize(deserializer)
        .map(|opt| opt.map(|one_or_many| one_or_many.into_vec()))
}

/// Button configuration
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct ButtonConfig {
    pub label: String,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub long_press_label: Option<String>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub long_press_color: Option<ButtonColor>,
    /// Whether to keep long_press_label visible indefinitely (default: true)
    /// When false, label shows for 3s then returns to selected button
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub long_press_label_persist: Option<bool>,
    /// Whether to keep conditional labels (then_label/else_label) visible (default: false)
    /// When false, label shows for 3s then returns to selected button
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub conditional_label_persist: Option<bool>,
    pub color: ButtonColor,

    // ===== DEVICE PROFILE SUPPORT =====
    /// Device profile ID (e.g., 'quad-cortex', 'helix')
    /// When set with action_id, editor resolves to MIDI before saving
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub profile_id: Option<String>,
    /// Action within profile (e.g., 'scene_b', 'snapshot_3')
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub action_id: Option<String>,

    // ===== NEW: Multi-command event arrays =====
    // Now supports conditional commands in addition to regular MIDI commands
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub press: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub release: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub long_press: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub long_release: Option<Vec<CommandOrConditional>>,
    #[ts(skip)]
    #[serde(
        default,
        skip_serializing_if = "Option::is_none",
        deserialize_with = "deserialize_one_or_many"
    )]
    pub double_press: Option<Vec<CommandOrConditional>>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub double_press_timeout_ms: Option<u16>,

    // ===== LEGACY: Single-type fields (for backwards compatibility) =====
    #[serde(
        rename = "type",
        default,
        skip_serializing_if = "is_default_message_type"
    )]
    pub message_type: MessageType,
    #[serde(default)]
    pub mode: ButtonMode,
    #[serde(default, skip_serializing_if = "is_default_off_mode")]
    pub off_mode: OffMode,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub dim_brightness: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channel: Option<u8>,
    // CC fields
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc_on: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc_off: Option<u8>,
    // Note fields
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub note: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub velocity_on: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub velocity_off: Option<u8>,
    // PC fields
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub program: Option<u8>,
    // PC inc/dec fields
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pc_step: Option<u8>,
    // PC flash feedback (all PC types)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub flash_ms: Option<u16>,

    // ===== SIMPLIFIED TOGGLE FIELDS =====
    // Used when mode='toggle' to auto-derive CC on/off without defining press/release arrays
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value_on: Option<u8>, // CC value sent when turning ON (default 127)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value_off: Option<u8>, // CC value sent when turning OFF (default 0)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub default_on: Option<bool>, // If true, button boots in ON state and sends value_on

    // ===== COMMON FIELDS =====
    // Keytimes cycling
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub keytimes: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub states: Option<Vec<StateOverride>>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub select_group: Option<String>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub default_selected: Option<bool>,
}

fn is_default_off_mode(mode: &OffMode) -> bool {
    *mode == OffMode::Dim
}

fn is_default_message_type(t: &MessageType) -> bool {
    *t == MessageType::Cc
}

/// Encoder push button configuration
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct EncoderPush {
    pub enabled: bool,
    pub cc: u8,
    pub label: String,
    #[serde(default)]
    pub mode: ButtonMode,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub channel: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub cc_on: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[ts(optional)]
    pub cc_off: Option<u8>,
}

/// Rotary encoder configuration (STD10 only)
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct EncoderConfig {
    pub enabled: bool,
    pub cc: u8,
    pub label: String,
    #[serde(default)]
    pub min: u8,
    #[serde(default = "default_max")]
    pub max: u8,
    #[serde(default = "default_initial")]
    pub initial: u8,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub steps: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub push: Option<EncoderPush>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channel: Option<u8>,
}

fn default_max() -> u8 {
    127
}
fn default_initial() -> u8 {
    64
}

/// Expression pedal configuration
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct ExpressionConfig {
    pub enabled: bool,
    pub cc: u8,
    pub label: String,
    #[serde(default)]
    pub min: u8,
    #[serde(default = "default_max")]
    pub max: u8,
    #[serde(default)]
    pub polarity: Polarity,
    #[serde(default = "default_threshold")]
    pub threshold: u8,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channel: Option<u8>,
}

fn default_threshold() -> u8 {
    2
}

/// Expression pedals container
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct ExpressionPedals {
    pub exp1: ExpressionConfig,
    pub exp2: ExpressionConfig,
}

/// Display text size settings
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct DisplayConfig {
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub button_text_size: Option<String>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status_text_size: Option<String>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expression_text_size: Option<String>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub button_name_text_size: Option<String>,
}

/// Splash screen configuration
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct SplashScreenConfig {
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub enabled: Option<bool>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub duration_ms: Option<u32>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub idle_timeout_seconds: Option<u32>,
}

/// Bank configuration for multi-bank mode
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct BankConfig {
    pub name: String,
    pub buttons: Vec<ButtonConfig>,
}

/// Bank switching configuration
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct BankSwitchConfig {
    #[serde(default = "default_bank_switch_method")]
    pub method: BankSwitchMethod,
    /// [Legacy] Single button cycles through banks
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub button: Option<u8>,
    /// Button for next bank (bank up) - takes precedence over 'button'
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub button_next: Option<u8>,
    /// Button for previous bank (bank down)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub button_prev: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cc: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pc_base: Option<u8>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channel: Option<u8>,
}

/// Complete MIDI Captain configuration
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct MidiCaptainConfig {
    #[serde(default)]
    pub device: DeviceType,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub global_channel: Option<u8>,
    /// Custom USB volume label (max 11 chars, alphanumeric + underscore).
    /// Applied by boot.py via storage.remount() when the drive is enabled.
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub usb_drive_name: Option<String>,
    /// Development mode: when true the USB drive always mounts on boot without
    /// needing to hold Switch 1.  Defaults to false (performance mode).
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub dev_mode: Option<bool>,
    /// MIDI output transport: "usb" (default), "trs", or "both".
    /// "usb"  — USB MIDI only (adafruit_midi over usb_midi.ports)
    /// "trs"  — TRS/serial MIDI only (UART on GP16/GP17 at 31250 baud)
    /// "both" — send to USB and TRS simultaneously
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub midi_transport: Option<String>,

    // ===== MULTI-BANK SUPPORT =====
    /// Array of banks (max 8 recommended for Flash storage)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub banks: Option<Vec<BankConfig>>,
    /// Bank switching configuration (method, button/CC/PC, channel)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bank_switch: Option<BankSwitchConfig>,
    /// Active bank on boot (0-indexed, default: 0)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub active_bank: Option<u8>,

    // ===== SINGLE-BANK MODE (legacy, backward compatibility) =====
    /// Legacy: single bank of buttons (auto-wrapped in banks[0] on load if banks not present)
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub buttons: Option<Vec<ButtonConfig>>,

    // ===== SHARED ACROSS ALL BANKS =====
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub encoder: Option<EncoderConfig>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expression: Option<ExpressionPedals>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub display: Option<DisplayConfig>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub splash_screen: Option<SplashScreenConfig>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub long_press_threshold_ms: Option<u32>,
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub double_press_timeout_ms: Option<u16>,
    /// Channel labels: optional mapping of channel numbers (as strings "0"-"15") to device names
    /// Example: { "0": "Quad Cortex", "1": "Timespace Delay" }
    /// Used in UI to show "Quad Cortex (Ch1)" instead of "Channel 1"
    /// Uses BTreeMap instead of HashMap to ensure stable, sorted JSON output
    #[ts(optional)]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub channel_labels: Option<std::collections::BTreeMap<String, String>>,
}

impl MidiCaptainConfig {
    /// Helper for tests: Get buttons from either banks[0] or legacy buttons field
    /// Returns reference to first bank's buttons if banks exist, otherwise legacy buttons
    #[cfg(test)]
    pub fn get_buttons(&self) -> &[ButtonConfig] {
        if let Some(ref banks) = self.banks {
            if !banks.is_empty() {
                return &banks[0].buttons;
            }
        }
        self.buttons.as_ref().map(|b| b.as_slice()).unwrap_or(&[])
    }

    /// Helper for tests: Mutable access to buttons
    #[cfg(test)]
    pub fn get_buttons_mut(&mut self) -> &mut Vec<ButtonConfig> {
        if let Some(ref mut banks) = self.banks {
            if !banks.is_empty() {
                return &mut banks[0].buttons;
            }
        }
        self.buttons.as_mut().unwrap()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_roundtrip_channel_labels() {
        // Test that channel_labels field survives deserialization/serialization
        let json = r#"{
            "device": "std10",
            "global_channel": 0,
            "channel_labels": {
                "0": "Quad Cortex",
                "1": "Timespace Delay",
                "2": "HX Stomp"
            },
            "buttons": []
        }"#;

        let config: MidiCaptainConfig = serde_json::from_str(json).expect("Failed to parse");
        assert!(config.channel_labels.is_some());
        let labels = config.channel_labels.as_ref().unwrap();
        assert_eq!(labels.get("0"), Some(&"Quad Cortex".to_string()));
        assert_eq!(labels.get("1"), Some(&"Timespace Delay".to_string()));
        assert_eq!(labels.get("2"), Some(&"HX Stomp".to_string()));

        let serialized = serde_json::to_string_pretty(&config).expect("Failed to serialize");
        assert!(serialized.contains("channel_labels"));
        assert!(serialized.contains("Quad Cortex"));
    }

    #[test]
    fn test_channel_labels_optional() {
        // Test that channel_labels is optional and doesn't appear when absent
        let json = r#"{
            "device": "std10",
            "global_channel": 0,
            "buttons": []
        }"#;

        let config: MidiCaptainConfig = serde_json::from_str(json).expect("Failed to parse");
        assert!(config.channel_labels.is_none());

        let serialized = serde_json::to_string_pretty(&config).expect("Failed to serialize");
        assert!(!serialized.contains("channel_labels")); // Should not appear when None
    }
}
