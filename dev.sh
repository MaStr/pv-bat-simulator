#!/bin/bash

# PV Battery Simulator - Development Helper Script
# Provides common commands for managing the local development environment

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}PV Battery Simulator - Development Helper${NC}"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}setup${NC}         - Set up virtual environment and install dependencies"
    echo -e "  ${GREEN}start${NC}         - Start the application server"
    echo -e "  ${GREEN}test${NC}          - Run tests (if available)"
    echo -e "  ${GREEN}clean${NC}         - Remove virtual environment and cache files"
    echo -e "  ${GREEN}install${NC}       - Install/reinstall dependencies"
    echo -e "  ${GREEN}shell${NC}         - Activate virtual environment in current shell"
    echo -e "  ${GREEN}info${NC}          - Show environment information"
    echo -e "  ${GREEN}help${NC}          - Show this help message"
    echo ""
}

check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Virtual environment not found. Run: ./dev.sh setup${NC}"
        exit 1
    fi
}

case "$1" in
    setup)
        ./run_local.sh
        ;;
    
    start)
        check_venv
        ./run_local.sh start
        ;;
    
    test)
        check_venv
        echo -e "${YELLOW}Running tests...${NC}"
        source "$VENV_DIR/bin/activate"
        if [ -f "test_app.py" ]; then
            python -m pytest test_app.py -v
        else
            echo -e "${YELLOW}No test file found${NC}"
        fi
        ;;
    
    clean)
        echo -e "${YELLOW}Cleaning up...${NC}"
        rm -rf "$VENV_DIR"
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        find . -type f -name "*.pyc" -delete 2>/dev/null
        echo -e "${GREEN}✓${NC} Cleaned virtual environment and cache files"
        ;;
    
    install)
        check_venv
        echo -e "${YELLOW}Installing/updating dependencies...${NC}"
        source "$VENV_DIR/bin/activate"
        pip install --upgrade pip wheel
        pip install --only-binary=:all: -r requirements.txt
        echo -e "${GREEN}✓${NC} Dependencies installed (binary wheels only)"
        ;;
    
    shell)
        check_venv
        echo -e "${GREEN}To activate the virtual environment, run:${NC}"
        echo -e "  ${BLUE}source venv/bin/activate${NC}"
        ;;
    
    info)
        echo -e "${BLUE}Environment Information:${NC}"
        echo ""
        if [ -d "$VENV_DIR" ]; then
            echo -e "Virtual environment: ${GREEN}✓ Exists${NC}"
            echo -e "Location: $VENV_DIR"
            source "$VENV_DIR/bin/activate"
            echo -e "Python version: $(python --version)"
            echo -e "Pip version: $(pip --version | cut -d' ' -f1-2)"
            echo ""
            echo -e "${BLUE}Installed packages:${NC}"
            pip list | grep -E "flask|pulp|numpy|pytz|cachetools|requests|batcontrol"
        else
            echo -e "Virtual environment: ${RED}✗ Not found${NC}"
            echo -e "Run: ${BLUE}./dev.sh setup${NC}"
        fi
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        if [ -z "$1" ]; then
            show_help
        else
            echo -e "${RED}Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
        fi
        ;;
esac
