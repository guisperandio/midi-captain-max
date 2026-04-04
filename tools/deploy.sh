#!/bin/bash
# Deploy firmware to MIDI Captain device
#
# Works from both development repository and distributed firmware package.
#
# Usage: ./deploy.sh [options] [mount_point]
#
# Options:
#   --install     Full install: check/install libraries first
#   --libs-only   Only install libraries (no firmware copy)
#   --eject       Eject device after deploy (forces clean reload)
#   --fresh       Overwrite config.json even if it exists
#   --dry-run     Preview changes without copying files
#   --code-only   Only deploy code.py (fastest iteration)
#   --skip-fonts  Skip font deployment
#   --skip-libs   Skip library deployment
#   --skip-config Skip config migration/deployment
#
# Examples:
#   ./deploy.sh                          # Quick deploy
#   ./deploy.sh --install                # Full install with libraries
#   ./deploy.sh --libs-only              # Just install CircuitPython libs
#   ./deploy.sh --eject                  # Deploy + eject (clean disconnect)
#   ./deploy.sh --fresh                  # Deploy + overwrite config
#   ./deploy.sh /Volumes/MIDICAPT        # Custom mount point
#
# Requires boot.py on device with autoreload disabled for best results.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Auto-detect context: development repo vs. distributed package
if [ -d "$PROJECT_ROOT/firmware/circuitpython" ]; then
    # Running from development repository
    DEV_DIR="$PROJECT_ROOT/firmware/circuitpython"
    CONTEXT="dev"
elif [ -f "$SCRIPT_DIR/code.py" ] || [ -d "$SCRIPT_DIR/firmware" ]; then
    # Running from distributed package (firmware files in same dir or firmware/ subdir)
    if [ -f "$SCRIPT_DIR/code.py" ]; then
        DEV_DIR="$SCRIPT_DIR"
    else
        DEV_DIR="$SCRIPT_DIR/firmware"
    fi
    CONTEXT="dist"
else
    echo -e "${RED}❌ Cannot locate firmware files${NC}"
    echo "Expected firmware/circuitpython/ (dev repo) or code.py (distributed package)"
    exit 1
fi

MOUNT_POINT="/Volumes/CIRCUITPY"
DO_EJECT=false
DO_RESET=false
DO_INSTALL=false
LIBS_ONLY=false
DO_FRESH=false
DO_DRY_RUN=false

# Skip options for faster iteration
SKIP_FONTS=false
SKIP_LIBS=false
SKIP_CONFIG=false
CODE_ONLY=false

# Timing tracking
DEPLOY_START_TIME=0
STEP_START_TIME=0

# Required CircuitPython libraries
REQUIRED_LIBS=(
    "adafruit_midi"
    "adafruit_display_text"
    "adafruit_st7789"
    "neopixel"
    "adafruit_debouncer"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
for arg in "$@"; do
    case $arg in
        --install)
            DO_INSTALL=true
            ;;
        --libs-only)
            LIBS_ONLY=true
            DO_INSTALL=true
            ;;
        --eject)
            DO_EJECT=true
            ;;
        --fresh)
            DO_FRESH=true
            ;;
        --dry-run)
            DO_DRY_RUN=true
            ;;
        --code-only)
            CODE_ONLY=true
            ;;
        --skip-fonts)
            SKIP_FONTS=true
            ;;
        --skip-libs)
            SKIP_LIBS=true
            ;;
        --skip-config)
            SKIP_CONFIG=true
            ;;
        --help|-h)
            echo "Usage: ./deploy.sh [options] [mount_point]"
            echo ""
            echo "Options:"
            echo "  --install     Full install: check/install libraries first"
            echo "  --libs-only   Only install libraries (no firmware copy)"
            echo "  --eject       Eject device after deploy (forces clean reload)"
            echo "  --fresh       Overwrite config.json even if it exists"
            echo "  --dry-run     Preview changes without copying files"
            echo ""
            echo "Speed Options (for development):"
            echo "  --code-only   Only deploy code.py (fastest: ~0.5s)"
            echo "  --skip-fonts  Skip font deployment"
            echo "  --skip-libs   Skip library deployment"
            echo "  --skip-config Skip config migration/deployment"
            echo ""
            echo "Works from both development repository and distributed package."
            exit 0
            ;;
        /*)
            MOUNT_POINT="$arg"
            ;;
    esac
done

echo -e "${BLUE}=== MIDI Captain Firmware Deploy ===${NC}"
echo ""

# Auto-detect mount point if not specified
if [ ! -d "$MOUNT_POINT" ]; then
    # Build candidate list: well-known defaults + usb_drive_name from local config files
    CANDIDATE_NAMES=("CIRCUITPY" "MIDICAPTAIN")
    for cfg_file in "$DEV_DIR/config.json" "$DEV_DIR/config-mini6.json"; do
        if [ -f "$cfg_file" ]; then
            # Parse usb_drive_name: use jq if available, fall back to grep/sed
            if command -v jq &>/dev/null; then
                CNAME=$(jq -r '.usb_drive_name // empty' "$cfg_file" 2>/dev/null)
            else
                CNAME=$(grep -o '"usb_drive_name"[[:space:]]*:[[:space:]]*"[^"]*"' "$cfg_file" 2>/dev/null \
                        | sed 's/.*"\([^"]*\)"$/\1/')
            fi
            if [ -n "$CNAME" ]; then
                # Add only if not already in the list
                if ! printf '%s\n' "${CANDIDATE_NAMES[@]}" | grep -qx "$CNAME"; then
                    CANDIDATE_NAMES+=("$CNAME")
                fi
            fi
        fi
    done

    # Collect volume root directories for this platform
    VOLUME_ROOTS=()
    [ -d "/Volumes" ] && VOLUME_ROOTS+=("/Volumes")
    if [ -n "${USER:-}" ]; then
        [ -d "/media/$USER" ]     && VOLUME_ROOTS+=("/media/$USER")
        [ -d "/run/media/$USER" ] && VOLUME_ROOTS+=("/run/media/$USER")
    fi

    # Try each candidate under each volume root
    for vol_root in "${VOLUME_ROOTS[@]}"; do
        for cname in "${CANDIDATE_NAMES[@]}"; do
            if [ -d "$vol_root/$cname" ]; then
                MOUNT_POINT="$vol_root/$cname"
                break 2
            fi
        done
    done
fi

# Check if device is mounted
if [ ! -d "$MOUNT_POINT" ]; then
    echo -e "${RED}❌ Device not found${NC}"
    echo ""
    # Build a readable list of paths that were tried
    TRIED_PATHS=()
    for vol_root in "${VOLUME_ROOTS[@]}"; do
        for cname in "${CANDIDATE_NAMES[@]}"; do
            TRIED_PATHS+=("$vol_root/$cname")
        done
    done
    echo "Tried: ${TRIED_PATHS[*]}"
    echo ""
    echo "Check that your device is plugged in, then:"
    # Show OS-appropriate commands
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  ls /Volumes/                        # see all mounted drives"
        echo "  ./deploy.sh /Volumes/MyDriveName    # specify a custom drive name"
    else
        # Linux
        echo "  ls /media/$USER/ /run/media/$USER/  # see all mounted drives"
        echo "  ./deploy.sh /media/$USER/MyDriveName  # specify a custom drive name"
    fi
    exit 1
fi

echo -e "${GREEN}✓ Device found at $MOUNT_POINT${NC}"

# Install libraries if requested
if [ "$DO_INSTALL" = true ]; then
    echo ""
    echo -e "${YELLOW}📦 Installing CircuitPython libraries...${NC}"
    
    # Check for circup
    if ! command -v circup &> /dev/null; then
        echo "  circup not found. Installing..."
        pip install circup --quiet
        if ! command -v circup &> /dev/null; then
            echo -e "${RED}✗ Failed to install circup${NC}"
            echo "  Try: pip install circup"
            exit 1
        fi
    fi
    echo -e "${GREEN}✓ circup available${NC}"
    
    # Install each library
    for lib in "${REQUIRED_LIBS[@]}"; do
        echo -n "  Installing $lib... "
        if circup install "$lib" --py 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            # Try without --py flag for compiled libs
            if circup install "$lib" 2>/dev/null; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${YELLOW}(already installed)${NC}"
            fi
        fi
    done
    echo -e "${GREEN}✓ Libraries installed${NC}"
    
    # Exit early if libs-only mode
    if [ "$LIBS_ONLY" = true ]; then
        echo ""
        echo -e "${GREEN}✅ Library installation complete!${NC}"
        exit 0
    fi
fi

echo ""
echo "📁 Source: $DEV_DIR"
echo "📱 Target: $MOUNT_POINT"
if [ "$CONTEXT" = "dev" ]; then
    echo "🔧 Mode: Development"
else
    echo "📦 Mode: Distribution package"
fi

# Detect device type from existing config on device, or by mount point
DEVICE_TYPE=""
if [ -f "$MOUNT_POINT/config.json" ]; then
    # Try to read device type from existing config
    DETECTED=$(grep -o '"device"[[:space:]]*:[[:space:]]*"[^"]*"' "$MOUNT_POINT/config.json" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
    if [ -n "$DETECTED" ]; then
        DEVICE_TYPE="$DETECTED"
    fi
fi

# Fallback: cannot determine device type without a config; default to std10
if [ -z "$DEVICE_TYPE" ]; then
    DEVICE_TYPE="std10"
fi

echo "🎛️  Device type: $DEVICE_TYPE"
echo ""

# Select appropriate config file
if [ "$DEVICE_TYPE" = "mini6" ]; then
    CONFIG_FILE="$DEV_DIR/config-mini6.json"
else
    CONFIG_FILE="$DEV_DIR/config.json"
fi

# Check if the device filesystem is writable before attempting deploy
if ! touch "$MOUNT_POINT/.deploy_write_test" 2>/dev/null; then
    echo -e "${RED}❌ Device filesystem is read-only${NC}"
    echo ""
    echo -e "${YELLOW}The MIDI Captain drive is mounted but not writable.${NC}"
    echo ""
    if [ -f "$MOUNT_POINT/boot.py" ]; then
        # boot.py exists: firmware already installed, device is in performance mode
        echo -e "${YELLOW}Our firmware is installed. To enable write access:${NC}"
        echo "  1. Hold switch 1 (top-left footswitch) while plugging in USB"
        echo "  2. The device will boot with USB write access enabled"
        echo "  3. Run deploy.sh again"
    else
        # No boot.py: likely first-time install over OEM firmware
        echo -e "${YELLOW}This looks like a first-time install.${NC}"
        echo "The OEM firmware may have the USB drive in read-only mode."
        echo ""
        echo -e "${YELLOW}Option A — CircuitPython safe mode (easiest):${NC}"
        echo "  1. Briefly short the RUN pin to GND twice in quick succession"
        echo "     (or rapidly plug/unplug USB twice if no RUN pin access)"
        echo "     Status LED will flash yellow — safe mode is active"
        echo "  2. Run deploy.sh again — the drive will be writable"
        echo ""
        echo -e "${YELLOW}Option B — Hold the update button during power-on:${NC}"
        echo "  1. Hold switch 1 (top-left footswitch) while plugging in USB"
        echo "  2. Run deploy.sh again"
        echo ""
        echo -e "${YELLOW}Option C — Reinstall CircuitPython:${NC}"
        echo "  1. Hold Switch 1 (top-left footswitch) while plugging in USB → RPI-RP2 drive appears"
        echo "  2. Copy CircuitPython .uf2 to the RPI-RP2 drive"
        echo "  3. Run deploy.sh again"
    fi
    exit 1
fi
rm -f "$MOUNT_POINT/.deploy_write_test" 2>/dev/null

# Check available disk space
echo "💾 Checking disk space..."
if command -v df &>/dev/null; then
    # Get available space in KB, cross-platform (works on macOS and Linux)
    AVAILABLE_KB=$(df -k "$MOUNT_POINT" | tail -1 | awk '{print $4}')
    AVAILABLE_MB=$((AVAILABLE_KB / 1024))
    
    # Firmware typically needs ~500KB-1MB
    MIN_REQUIRED_MB=1
    
    if [ "$AVAILABLE_MB" -lt "$MIN_REQUIRED_MB" ]; then
        echo -e "${RED}❌ Insufficient disk space!${NC}"
        echo "   Available: ${AVAILABLE_MB} MB"
        echo "   Required: ${MIN_REQUIRED_MB} MB minimum"
        echo ""
        echo "Free up space on the device and try again."
        exit 1
    else
        echo -e "${GREEN}✓ ${AVAILABLE_MB} MB available${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Could not check disk space (df not available)${NC}"
fi
echo ""

# Start timing
DEPLOY_START_TIME=$(date +%s)

if [ "$DO_DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN MODE - No files will be copied${NC}"
    echo ""
fi

if [ "$CODE_ONLY" = true ]; then
    echo -e "${BLUE}⚡ CODE-ONLY MODE - Deploying code.py only (fastest)${NC}"
    echo ""
fi

echo "🚀 Deploying changed files..."
echo ""

# Calculate total steps based on what's being deployed
TOTAL_STEPS=7
if [ "$CODE_ONLY" = true ]; then
    TOTAL_STEPS=2  # VERSION + code.py
elif [ "$SKIP_FONTS" = true ] && [ "$SKIP_LIBS" = true ]; then
    TOTAL_STEPS=6  # Remove fonts/libs step
elif [ "$SKIP_CONFIG" = true ]; then
    TOTAL_STEPS=6  # Remove config step
fi

CURRENT_STEP=0

# Helper function to show progress with timing
show_progress() {
    if [ "$STEP_START_TIME" -ne 0 ]; then
        # Show elapsed time for previous step
        local step_end=$(date +%s)
        local step_duration=$((step_end - STEP_START_TIME))
        echo -e " ${BLUE}(${step_duration}s)${NC}"
    fi
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo -ne "${BLUE}[$CURRENT_STEP/$TOTAL_STEPS]${NC} $1"
    STEP_START_TIME=$(date +%s)
}

# Helper to add dry-run flag if enabled
rsync_flags() {
    local flags="-a --checksum --inplace --itemize-changes"
    if [ "$DO_DRY_RUN" = true ]; then
        flags="$flags --dry-run"
    fi
    echo "$flags"
}

# Deploy dependencies first, code.py last. This ensures all imports are
# in place before the main entry point lands on the device.
#
# NOTE: This script deploys raw .py source files for rapid development.
# CI builds compile core/ and devices/ to .mpy bytecode for smaller/faster
# production firmware. See .github/workflows/ci.yml for the compile step.
#
# rsync flags:
# -a: archive mode (preserve permissions)
# --checksum: compare by content hash, not timestamp (only copies changed files)
# --inplace: minimize file rewrites
# --itemize-changes: show what changed (suppresses output for unchanged files)
# No -v flag: reduces noise, only shows actual changes via --itemize-changes

# Track changed files for summary
CHANGED_FILES=0

# 1. boot.py first (keeps autoreload disabled)
if [ "$CODE_ONLY" != true ]; then
    show_progress "Deploying boot.py..."
    BOOT_CHANGES=$(rsync $(rsync_flags) \
        "$DEV_DIR/boot.py" \
        "$MOUNT_POINT/" | grep -c '^>' || true)
    CHANGED_FILES=$((CHANGED_FILES + BOOT_CHANGES))
fi

# 2. Core modules, device definitions, and handlers
if [ "$CODE_ONLY" != true ]; then
    show_progress "Deploying core modules, devices, handlers..."
    # --delete removes stale files from the device (e.g. old .py source when
    # deploying compiled .mpy from a package, or old .mpy when deploying .py
    # source from the dev repo). Without --delete, both forms can coexist on
    # the device and CircuitPython may load the wrong one, causing ImportErrors.
CORE_CHANGES=$(rsync $(rsync_flags) --delete \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "$DEV_DIR/core/" "$MOUNT_POINT/core/" | grep -c '^[>*]' || true)
CHANGED_FILES=$((CHANGED_FILES + CORE_CHANGES))

DEVICES_CHANGES=$(rsync $(rsync_flags) --delete \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "$DEV_DIR/devices/" "$MOUNT_POINT/devices/" | grep -c '^[>*]' || true)
CHANGED_FILES=$((CHANGED_FILES + DEVICES_CHANGES))

HANDLERS_CHANGES=$(rsync $(rsync_flags) --delete \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "$DEV_DIR/handlers/" "$MOUNT_POINT/handlers/" | grep -c '^[>*]' || true)
CHANGED_FILES=$((CHANGED_FILES + HANDLERS_CHANGES))
fi

# 3. Fonts and libraries (deployed in parallel for speed)
if [ "$CODE_ONLY" != true ] && { [ "$SKIP_FONTS" != true ] || [ "$SKIP_LIBS" != true ]; }; then
    show_progress "Deploying fonts and libraries..."
    
    # Deploy fonts and libs in parallel (they don't depend on each other)
    if [ "$SKIP_FONTS" != true ]; then
        (
            rsync $(rsync_flags) \
                --exclude='.DS_Store' \
                "$DEV_DIR/fonts/" "$MOUNT_POINT/fonts/" > /tmp/deploy_fonts.$$ 2>&1
        ) &
        FONTS_PID=$!
    fi
    
    if [ "$SKIP_LIBS" != true ]; then
        (
            rsync $(rsync_flags) \
                --exclude='.DS_Store' \
                "$DEV_DIR/lib/" "$MOUNT_POINT/lib/" > /tmp/deploy_libs.$$ 2>&1
        ) &
        LIBS_PID=$!
    fi

    # Wait for both to complete
    [ -n "$FONTS_PID" ] && wait $FONTS_PID
    [ -n "$LIBS_PID" ] && wait $LIBS_PID

    # Count changes from temp files
    if [ "$SKIP_FONTS" != true ]; then
        FONTS_CHANGES=$(grep -c '^>' /tmp/deploy_fonts.$$ 2>/dev/null || echo 0)
        CHANGED_FILES=$((CHANGED_FILES + FONTS_CHANGES))
    fi
    
    if [ "$SKIP_LIBS" != true ]; then
        LIB_CHANGES=$(grep -c '^>' /tmp/deploy_libs.$$ 2>/dev/null || echo 0)
        CHANGED_FILES=$((CHANGED_FILES + LIB_CHANGES))
    fi

    # Cleanup temp files
    rm -f /tmp/deploy_fonts.$$ /tmp/deploy_libs.$$
fi

sync

# 4. Migrate existing config to latest format (if needed)
if [ "$CODE_ONLY" != true ] && [ "$SKIP_CONFIG" != true ]; then
    show_progress "Checking configuration..."
    if [ -f "$MOUNT_POINT/config.json" ] && [ "$DO_FRESH" != true ]; then
        if command -v python3 >/dev/null 2>&1; then
            # Run migration script
            if python3 "$SCRIPT_DIR/migrate_config.py" "$MOUNT_POINT" "$CONFIG_FILE" 2>&1; then
                echo "  ✓ Config migration complete"
            else
                echo -e "  ${YELLOW}⚠ Config migration skipped (migration script not available)${NC}"
            fi
        else
            echo -e "  ${YELLOW}⚠ Python3 not found, skipping config migration${NC}"
        fi
    else
        # No existing config or fresh mode - skip migration
        if [ "$DO_FRESH" = true ]; then
            echo "  Fresh mode: will install clean config"
        fi
    fi
fi

# 5. Deploy config ONLYif it doesn't exist (preserve user customizations)
if [ "$CODE_ONLY" != true ] && [ "$SKIP_CONFIG" != true ]; then
    show_progress "Deploying configuration files..."
    if [ ! -f "$MOUNT_POINT/config.json" ] || [ "$DO_FRESH" = true ]; then
        if [ "$DO_FRESH" = true ] && [ -f "$MOUNT_POINT/config.json" ]; then
            echo "  Overwriting config.json with fresh default (--fresh mode)"
        else
            echo "  Installing default config.json (device-specific)"
        fi
        if [ -f "$CONFIG_FILE" ]; then
            CONFIG_CHANGE=$(rsync $(rsync_flags) \
                "$CONFIG_FILE" "$MOUNT_POINT/config.json" | grep -c '^>' || true)
            CHANGED_FILES=$((CHANGED_FILES + CONFIG_CHANGE))
        else
            CONFIG_CHANGE=$(rsync $(rsync_flags) \
                "$DEV_DIR/config.json" "$MOUNT_POINT/config.json" | grep -c '^>' || true)
            CHANGED_FILES=$((CHANGED_FILES + CONFIG_CHANGE))
        fi
    else
        echo "  Preserving existing config.json (use --fresh to overwrite)"
    fi

    # Deploy device-specific fallback config (reference only)
    MINI6_CHANGES=$(rsync $(rsync_flags) \
        "$DEV_DIR/config-mini6.json" "$MOUNT_POINT/config-mini6.json" | grep -c '^>' || true)
    CHANGED_FILES=$((CHANGED_FILES + MINI6_CHANGES))
fi

# 6. code.py LAST (all dependencies are now in place)
show_progress "Deploying main firmware (code.py)..."
CODE_CHANGES=$(rsync $(rsync_flags) \
    --exclude='.DS_Store' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='experiments' \
    "$DEV_DIR/code.py" \
    "$MOUNT_POINT/" | grep -c '^>' || true)
CHANGED_FILES=$((CHANGED_FILES + CODE_CHANGES))

# 7. Write VERSION file for firmware version display
show_progress "Writing version information..."
# Distributed packages include a pre-built VERSION file written by CI.
# Use it directly rather than falling back to "dev" via git describe.
if [ "$CONTEXT" = "dist" ] && [ -f "$DEV_DIR/VERSION" ]; then
    VERSION=$(cat "$DEV_DIR/VERSION")
    VERSION_CHANGE=$(rsync $(rsync_flags) \
        "$DEV_DIR/VERSION" "$MOUNT_POINT/VERSION" | grep -c '^>' || true)
    CHANGED_FILES=$((CHANGED_FILES + VERSION_CHANGE))
else
    VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")
    # Check if VERSION needs updating (skip in dry-run mode)
    if [ "$DO_DRY_RUN" != true ]; then
        if [ -f "$MOUNT_POINT/VERSION" ]; then
            CURRENT_VERSION=$(cat "$MOUNT_POINT/VERSION" 2>/dev/null || echo "")
            if [ "$VERSION" != "$CURRENT_VERSION" ]; then
                echo "$VERSION" > "$MOUNT_POINT/VERSION"
                echo "$VERSION" > "$DEV_DIR/VERSION"
                CHANGED_FILES=$((CHANGED_FILES + 1))
            fi
        else
            echo "$VERSION" > "$MOUNT_POINT/VERSION"
            echo "$VERSION" > "$DEV_DIR/VERSION"
            CHANGED_FILES=$((CHANGED_FILES + 1))
        fi
    fi
fi
echo "  Version: $VERSION"

# Sync filesystem
sync

# Generate manifest on device for incremental installer updates.
# The installer compares this against the firmware zip's manifest
# to skip unchanged files on subsequent installs.
if [ "$CODE_ONLY" != true ]; then
    show_progress "Generating firmware manifest..."
    # Detect checksum command: md5sum (Linux) or md5 -r (macOS)
    if command -v md5sum &>/dev/null; then
        MD5_CMD="md5sum"
    elif command -v md5 &>/dev/null; then
        MD5_CMD="md5 -r"
    else
        MD5_CMD=""
    fi
    if [ -n "$MD5_CMD" ]; then
        (
          cd "$DEV_DIR"
          find . -type f \
            -not -name "*.pyc" \
            -not -path "*/__pycache__/*" \
            -not -path "*/experiments/*" \
            -not -name "firmware.md5" \
            -not -name ".DS_Store" \
            | sort \
            | xargs $MD5_CMD > "$MOUNT_POINT/firmware.md5"
        )
    else
        echo "  ⚠️  Skipping (checksum tool not found)"
    fi
fi

# Show timing for last step
if [ "$STEP_START_TIME" -ne 0 ]; then
    local step_end=$(date +%s)
    local step_duration=$((step_end - STEP_START_TIME))
    echo -e " ${BLUE}(${step_duration}s)${NC}"
fi

# Calculate total deployment time
DEPLOY_END_TIME=$(date +%s)
TOTAL_TIME=$((DEPLOY_END_TIME - DEPLOY_START_TIME))

# Print deployment summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$DO_DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN COMPLETE${NC}"
    if [ "$CHANGED_FILES" -eq 0 ]; then
        echo "   No changes detected"
    else
        echo "   $CHANGED_FILES file(s) would be updated"
    fi
elif [ "$CHANGED_FILES" -eq 0 ]; then
    echo -e "${GREEN}✨ Deployment complete — No changes needed${NC}"
    echo "   Device is already up to date"
else
    echo -e "${GREEN}✅ Deployment complete — Updated $CHANGED_FILES file(s)${NC}"
fi
echo -e "${BLUE}⏱️  Total time: ${TOTAL_TIME}s${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$DO_EJECT" = true ]; then
    echo "⏏️  Ejecting device..."
    diskutil eject "$MOUNT_POINT" 2>/dev/null || true
    echo ""
    echo "Reconnect device to start firmware."
else
    echo "To reload the firmware:"
    echo "  • Open serial console and press Ctrl+D"
    echo "  • Or: Power-cycle the device"
    echo "  • Or: Re-run with --eject to force clean reload"
fi
