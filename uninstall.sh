#!/bin/bash
# Uninstall smileymath

set -e

INSTALL_DIR="/opt/smileymath"
BIN_LINK="/usr/local/bin/smileymath"

if [ "$(id -u)" -ne 0 ]; then
    echo "This script requires root privileges. Re-running with sudo..."
    exec sudo "$0" "$@"
fi

echo "Uninstalling smileymath..."
rm -rf "${INSTALL_DIR}"
rm -f "${BIN_LINK}"
echo "Done. smileymath has been removed."
