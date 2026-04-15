#!/usr/bin/env python3
"""
MIDI Captain Config Validator CLI

Validates configuration files for MIDI Captain firmware.
Provides detailed error messages and configuration statistics.

Usage:
    python3 tools/validate_config.py config.json
    python3 tools/validate_config.py firmware/circuitpython/config.json
    python3 tools/validate_config.py --check-all  # validate all configs in repo

Exit codes:
    0 - Valid configuration
    1 - Invalid configuration or file error
    2 - Multiple configs checked, some invalid
"""

import sys
import json
import os
from pathlib import Path

# Add firmware modules to path
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
FIRMWARE_DIR = REPO_ROOT / "firmware" / "circuitpython"
sys.path.insert(0, str(FIRMWARE_DIR / "core"))

try:
    from config import validate_config, validate_button
except ImportError as e:
    print(f"❌ Failed to import validation modules: {e}", file=sys.stderr)
    print(f"   Make sure you're running from the repository root", file=sys.stderr)
    sys.exit(1)


def count_commands(config):
    """Count total MIDI commands across all buttons and events."""
    total = 0
    buttons = config.get("buttons", [])
    
    for btn in buttons:
        # Count event array commands
        for event_key in ["press", "release", "long_press", "long_release"]:
            event = btn.get(event_key)
            if isinstance(event, list):
                total += len(event)
            elif isinstance(event, dict):
                total += 1
        
        # Count keytime state overrides
        states = btn.get("states", [])
        if isinstance(states, list):
            for state in states:
                if isinstance(state, dict):
                    # Each state can override commands
                    for event_key in ["press", "release", "long_press", "long_release"]:
                        if event_key in state:
                            event = state[event_key]
                            if isinstance(event, list):
                                total += len(event)
                            elif isinstance(event, dict):
                                total += 1
    
    # Count encoder commands
    encoder = config.get("encoder", {})
    if encoder.get("enabled"):
        total += 1  # encoder CC
        push = encoder.get("push", {})
        if push.get("enabled"):
            total += 2  # push on/off
    
    # Count expression pedal commands
    expression = config.get("expression", {})
    for pedal_key in ["exp1", "exp2"]:
        pedal = expression.get(pedal_key, {})
        if pedal.get("enabled"):
            total += 1
    
    return total


def count_conditional_blocks(config):
    """Count conditional action blocks."""
    total = 0
    buttons = config.get("buttons", [])
    
    for btn in buttons:
        for event_key in ["press", "release", "long_press", "long_release"]:
            commands = btn.get(event_key, [])
            if isinstance(commands, list):
                for cmd in commands:
                    if isinstance(cmd, dict) and "condition" in cmd:
                        total += 1
    
    return total


def analyze_config(config):
    """Generate configuration statistics."""
    device = config.get("device", "unknown")
    button_count = len(config.get("buttons", []))
    command_count = count_commands(config)
    conditional_count = count_conditional_blocks(config)
    
    # Count keytimes usage
    keytimes_buttons = sum(
        1 for btn in config.get("buttons", [])
        if btn.get("keytimes", 1) > 1
    )
    
    # Count select groups
    select_groups = set()
    for btn in config.get("buttons", []):
        sg = btn.get("select_group")
        if sg:
            select_groups.add(sg)
    
    # Check banks/pages
    banks = config.get("banks", [])
    is_multi_bank = len(banks) > 0
    bank_count = len(banks) if is_multi_bank else 1
    
    stats = {
        "device": device,
        "button_count": button_count,
        "command_count": command_count,
        "conditional_count": conditional_count,
        "keytimes_buttons": keytimes_buttons,
        "select_group_count": len(select_groups),
        "is_multi_bank": is_multi_bank,
        "bank_count": bank_count,
    }
    
    return stats


def validate_config_file(config_path):
    """Validate a single config file."""
    path = Path(config_path)
    
    if not path.exists():
        print(f"❌ File not found: {config_path}", file=sys.stderr)
        return False
    
    try:
        with open(path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_path}:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Failed to read {config_path}:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        return False
    
    # Validate structure
    try:
        validated_config = validate_config(config)
    except Exception as e:
        print(f"❌ Validation failed for {config_path}:", file=sys.stderr)
        print(f"   {e}", file=sys.stderr)
        return False
    
    # Analyze configuration
    stats = analyze_config(validated_config)
    
    # Print results
    print(f"✅ Valid configuration for {stats['device'].upper()} device")
    print(f"📊 Statistics:")
    
    if stats['is_multi_bank']:
        print(f"   • Banks: {stats['bank_count']}")
    
    print(f"   • Buttons: {stats['button_count']}")
    print(f"   • Total MIDI commands: {stats['command_count']}")
    
    if stats['conditional_count'] > 0:
        print(f"   • Conditional blocks: {stats['conditional_count']}")
    
    if stats['keytimes_buttons'] > 0:
        print(f"   • Buttons with keytimes: {stats['keytimes_buttons']}")
    
    if stats['select_group_count'] > 0:
        print(f"   • Select groups: {stats['select_group_count']}")
    
    # Check for potential issues
    warnings = []
    
    # Check for buttons using CC 127 (at upper limit)
    for btn in validated_config.get("buttons", []):
        for event_key in ["press", "release"]:
            commands = btn.get(event_key, [])
            if isinstance(commands, dict):
                commands = [commands]
            if isinstance(commands, list):
                for cmd in commands:
                    if isinstance(cmd, dict):
                        cc = cmd.get("cc")
                        value = cmd.get("value", cmd.get("cc_on"))
                        if cc == 127:
                            warnings.append(f"Button '{btn.get('label', '?')}' uses CC 127 (upper limit)")
                        if value == 127 and cmd.get("type", "cc") == "cc":
                            pass  # This is normal for toggle on
    
    # Check for dense CC usage (potential conflicts)
    used_ccs = set()
    for btn in validated_config.get("buttons", []):
        for event_key in ["press"]:
            commands = btn.get(event_key, [])
            if isinstance(commands, dict):
                commands = [commands]
            if isinstance(commands, list):
                for cmd in commands:
                    if isinstance(cmd, dict) and cmd.get("type", "cc") == "cc":
                        cc = cmd.get("cc")
                        if cc is not None:
                            used_ccs.add(cc)
    
    if len(used_ccs) > 64:
        warnings.append(f"{len(used_ccs)} unique CCs used (potential for conflicts)")
    
    if warnings:
        print(f"\n⚠️  Warnings:")
        for w in warnings:
            print(f"   • {w}")
    
    print()  # blank line
    return True


def find_all_configs():
    """Find all config.json and config-*.json files in the repository."""
    config_files = []
    
    # Check firmware directory
    firmware_dir = FIRMWARE_DIR
    if firmware_dir.exists():
        config_files.extend(firmware_dir.glob("config*.json"))
    
    # Check root directory
    config_files.extend(REPO_ROOT.glob("config*.json"))
    
    return sorted(set(config_files))


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate MIDI Captain configuration files",
        epilog="Examples:\n"
               "  %(prog)s config.json\n"
               "  %(prog)s firmware/circuitpython/config.json\n"
               "  %(prog)s --check-all",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        help="Path to config.json file to validate"
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Validate all config files found in repository"
    )
    
    args = parser.parse_args()
    
    if args.check_all:
        configs = find_all_configs()
        if not configs:
            print("❌ No config files found in repository", file=sys.stderr)
            return 2
        
        print(f"🔍 Found {len(configs)} config file(s) to validate\n")
        
        results = []
        for config_path in configs:
            print(f"Validating {config_path.relative_to(REPO_ROOT)}...")
            result = validate_config_file(config_path)
            results.append((config_path, result))
        
        # Summary
        valid_count = sum(1 for _, r in results if r)
        invalid_count = len(results) - valid_count
        
        print("=" * 60)
        print(f"Summary: {valid_count} valid, {invalid_count} invalid")
        
        if invalid_count > 0:
            print("\n❌ Invalid configurations:")
            for path, result in results:
                if not result:
                    print(f"   • {path.relative_to(REPO_ROOT)}")
            return 2
        else:
            print("\n✅ All configurations valid!")
            return 0
    
    elif args.config_file:
        result = validate_config_file(args.config_file)
        return 0 if result else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
