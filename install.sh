#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/ai-router"

mkdir -p "$BIN_DIR"
mkdir -p "$CONFIG_DIR"

echo "Installing ai-router to $BIN_DIR..."

if [ -L "$BIN_DIR/ai" ]; then
    rm "$BIN_DIR/ai"
fi
ln -s "$SCRIPT_DIR/ai_router.py" "$BIN_DIR/ai"

if [ -L "$CONFIG_DIR/config.toml" ]; then
    rm "$CONFIG_DIR/config.toml"
fi
ln -s "$SCRIPT_DIR/config.toml" "$CONFIG_DIR/config.toml"

if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    echo "Added ~/.local/bin to PATH in $SHELL_RC"
fi

echo "Installation complete!"
echo "Restart your shell or run: source $SHELL_RC"
echo "Then use: ai \"your query\""
