#!/bin/bash
# Build and run automation for Asteroids game

set -e

# Build for Windows (.exe) using PyInstaller
build_exe() {
    echo "Building Windows executable with PyInstaller..."
    pyinstaller --onefile --windowed main.py
    echo "Executable created in dist/main.exe"
}

# Build for Web using Pygbag
build_web() {
    echo "Building web version with Pygbag..."
    pygbag --build main.py
    echo "Web build complete. See dist/ folder for index.html."
}

# Usage info
usage() {
    echo "Usage: $0 [exe|web]"
    echo "  exe  Build Windows executable (.exe) using PyInstaller"
    echo "  web  Build browser version using Pygbag"
}

# Main logic
if [ "$1" == "exe" ]; then
    build_exe
elif [ "$1" == "web" ]; then
    build_web
else
    usage
fi
