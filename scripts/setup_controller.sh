#!/bin/bash
# Helper script to copy POX controller to POX directory

# Default values
CONTROLLER="flood_cont"
POX_DIR="$HOME/pox"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--controller)
            CONTROLLER="$2"
            shift 2
            ;;
        -p|--pox-dir)
            POX_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -c, --controller   Controller to copy (flood_cont or rate_limit)"
            echo "  -p, --pox-dir      POX installation directory (default: ~/pox)"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if controller file exists
CONTROLLER_FILE="$PROJECT_ROOT/src/controllers/${CONTROLLER}.py"
if [ ! -f "$CONTROLLER_FILE" ]; then
    echo "Error: Controller file not found: $CONTROLLER_FILE"
    exit 1
fi

# Check if POX directory exists
if [ ! -d "$POX_DIR" ]; then
    echo "Error: POX directory not found: $POX_DIR"
    echo "Please install POX or specify the correct path with -p option"
    exit 1
fi

# Copy controller to POX misc directory
POX_MISC_DIR="$POX_DIR/pox/misc"
mkdir -p "$POX_MISC_DIR"
cp "$CONTROLLER_FILE" "$POX_MISC_DIR/"

echo "Successfully copied ${CONTROLLER}.py to $POX_MISC_DIR"
echo ""
echo "To start the controller, run:"
echo "  cd $POX_DIR"
echo "  ./pox.py log.level --DEBUG misc.${CONTROLLER}"

