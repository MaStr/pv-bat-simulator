#!/bin/bash

# PV Battery Simulator - Local Development Setup Script
# This script sets up a Python virtual environment and installs all dependencies

set -e  # Exit on error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
BATCONTROL_DIR="$PROJECT_DIR/.x./batcontrol"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PV Battery Simulator - Local Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Found: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip and install wheel
echo -e "${YELLOW}Upgrading pip and installing wheel...${NC}"
pip install --upgrade pip wheel > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip and wheel upgraded"

# Install batcontrol dependency
echo -e "${YELLOW}Installing batcontrol...${NC}"

# First, try to install from local source if available
if [ -d "$BATCONTROL_DIR" ]; then
    echo -e "${BLUE}  Found local batcontrol at: $BATCONTROL_DIR${NC}"
    if [ -f "$BATCONTROL_DIR/pyproject.toml" ]; then
        pip install --extra-index-url https://piwheels.org/simple -e "$BATCONTROL_DIR" > /dev/null 2>&1
        echo -e "${GREEN}✓${NC} batcontrol installed from local source (editable mode)"
    elif [ -f "$BATCONTROL_DIR/setup.py" ]; then
        pip install --extra-index-url https://piwheels.org/simple -e "$BATCONTROL_DIR" > /dev/null 2>&1
        echo -e "${GREEN}✓${NC} batcontrol installed from local source (editable mode)"
    else
        echo -e "${YELLOW}  No setup file found in local directory${NC}"
        if [ -d "$BATCONTROL_DIR/src/batcontrol" ]; then
            export PYTHONPATH="$BATCONTROL_DIR/src:$PYTHONPATH"
            echo -e "${GREEN}✓${NC} Added batcontrol src to PYTHONPATH"
        fi
    fi
else
    # If no local source, download wheel from GitHub
    echo -e "${BLUE}  Local source not found, downloading from GitHub...${NC}"
    BATCONTROL_VERSION="0.5.5"
    BATCONTROL_WHEEL="batcontrol-${BATCONTROL_VERSION}-py3-none-any.whl"
    BATCONTROL_URL="https://github.com/muexxl/batcontrol/releases/download/${BATCONTROL_VERSION}/${BATCONTROL_WHEEL}"
    
    if command -v wget &> /dev/null; then
        wget -q "$BATCONTROL_URL" -O "$VENV_DIR/$BATCONTROL_WHEEL"
    elif command -v curl &> /dev/null; then
        curl -sL "$BATCONTROL_URL" -o "$VENV_DIR/$BATCONTROL_WHEEL"
    else
        echo -e "${RED}Error: Neither wget nor curl found. Cannot download batcontrol.${NC}"
        echo -e "${YELLOW}  The simulator will work but Model 4 (BatControl) will not be available${NC}"
    fi
    
    if [ -f "$VENV_DIR/$BATCONTROL_WHEEL" ]; then
        pip install --extra-index-url https://piwheels.org/simple "$VENV_DIR/$BATCONTROL_WHEEL" > /dev/null 2>&1
        rm "$VENV_DIR/$BATCONTROL_WHEEL"
        echo -e "${GREEN}✓${NC} batcontrol ${BATCONTROL_VERSION} installed from GitHub"
    else
        echo -e "${YELLOW}⚠${NC}  Failed to download batcontrol wheel file"
        echo -e "    The simulator will work but Model 4 (BatControl) will not be available"
    fi
fi

# Install requirements (only binary wheels, no compilation)
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    # Install with only-binary to force binary wheels (fail if not available)
    pip install --only-binary=:all: -r "$PROJECT_DIR/requirements.txt"
    echo -e "${GREEN}✓${NC} All dependencies installed (binary wheels only)"
else
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Virtual environment: ${GREEN}$VENV_DIR${NC}"
echo -e "Python path: ${GREEN}$(which python)${NC}"
echo ""
echo -e "${YELLOW}To start the application:${NC}"
echo -e "  ${BLUE}./run_local.sh start${NC}"
echo ""
echo -e "${YELLOW}To manually activate the environment:${NC}"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "  ${BLUE}python app.py${NC}"
echo ""
echo -e "${YELLOW}To deactivate:${NC}"
echo -e "  ${BLUE}deactivate${NC}"
echo ""

# If 'start' argument is provided, run the application
if [ "$1" == "start" ]; then
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Starting PV Battery Simulator...${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}Application will be available at:${NC}"
    echo -e "  ${BLUE}http://localhost:5000${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Add batcontrol src to PYTHONPATH if needed
    if [ -d "$BATCONTROL_DIR/src" ]; then
        export PYTHONPATH="$BATCONTROL_DIR/src:$PYTHONPATH"
    fi
    
    python app.py
fi
