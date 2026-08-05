#!/bin/bash
# Install smileymath system-wide with a virtual environment backend
# Works on systems that block direct pip installs (externally-managed-environment)

set -e

INSTALL_DIR="/opt/smileymath"
BIN_LINK="/usr/local/bin/smileymath"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing smileymath..."

# Check for root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script requires root privileges. Re-running with sudo..."
    exec sudo "$0" "$@"
fi

# Install python3-venv if needed (Debian/Ubuntu)
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "Installing python3-venv..."
    apt-get install -y python3-venv 2>/dev/null || true
fi

# Create a dedicated virtual environment
echo "Creating virtual environment in ${INSTALL_DIR}..."
rm -rf "${INSTALL_DIR}"
python3 -m venv "${INSTALL_DIR}"

# Install smileymath into the venv
echo "Installing smileymath into virtual environment..."
"${INSTALL_DIR}/bin/pip" install --upgrade pip
"${INSTALL_DIR}/bin/pip" install "${SCRIPT_DIR}"

# Create a symlink so the command is on PATH
echo "Creating command symlink at ${BIN_LINK}..."
ln -sf "${INSTALL_DIR}/bin/smileymath" "${BIN_LINK}"

echo ""
echo "Done! You can now run: smileymath"
echo "  smileymath          - Start the GUI"
echo "  smileymath --ce1    - CE1 challenges"
echo "  smileymath --cm1    - CM1 challenges"
