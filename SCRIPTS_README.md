# Local Development Scripts

This directory contains scripts for setting up and running the PV Battery Simulator locally without Docker.

## Quick Start

### First Time Setup

```bash
# Clone or navigate to the project
cd /home/matze/projects/pv-bat-simulator

# Run setup (creates venv and installs dependencies)
./run_local.sh

# Or use the dev helper
./dev.sh setup
```

### Start the Application

```bash
# Start the server
./run_local.sh start

# Or use the dev helper
./dev.sh start
```

The application will be available at: **http://localhost:5000**

## Scripts Overview

### `run_local.sh` - Main Setup & Run Script

The primary script for setting up and running the application.

**Usage:**
```bash
./run_local.sh          # Setup only
./run_local.sh start    # Setup and start server
```

**What it does:**
1. Checks for Python 3 installation
2. Creates a virtual environment in `./venv/`
3. Upgrades pip and installs wheel package
4. Installs batcontrol:
   - First tries local source from `../batcontrol/bc-git-upstream-main` (editable mode)
   - If not found, downloads wheel file from GitHub (version 0.5.5)
5. Installs all dependencies from `requirements.txt` (prefers binary wheels for faster installation)
6. Optionally starts the Flask development server

**Features:**
- ✅ Colored output for better readability
- ✅ Error handling (exits on any error)
- ✅ Checks for existing virtual environment
- ✅ Automatically handles batcontrol dependency (local or GitHub)
- ✅ Downloads batcontrol wheel from GitHub if local source not available
- ✅ Supports both `pyproject.toml` and `setup.py` for local batcontrol
- ✅ Falls back to PYTHONPATH if batcontrol has no setup file
- ✅ Works with both wget and curl for downloads
- ✅ Prefers binary wheels for faster installation (avoids compilation)

### `dev.sh` - Development Helper

Convenient wrapper for common development tasks.

**Commands:**

```bash
./dev.sh setup          # Set up virtual environment
./dev.sh start          # Start the application
./dev.sh test           # Run tests
./dev.sh clean          # Remove venv and cache files
./dev.sh install        # Reinstall dependencies
./dev.sh shell          # Show how to activate venv
./dev.sh info           # Display environment information
./dev.sh help           # Show help message
```

**Examples:**

```bash
# Clean start
./dev.sh clean
./dev.sh setup
./dev.sh start

# Check environment
./dev.sh info

# Update dependencies
./dev.sh install
```

## Directory Structure

After running the setup, your directory will look like:

```
pv-bat-simulator/
├── venv/                   # Virtual environment (created by script)
│   ├── bin/
│   ├── lib/
│   └── ...
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
├── run_local.sh           # Setup & run script
├── dev.sh                 # Development helper
└── SCRIPTS_README.md      # This file
```

## Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **pip** (Python package installer)
- **bash** (for running the scripts)

The scripts will automatically install:
- flask==3.0.0
- pulp==2.7.0
- numpy==1.26.2
- pytz==2023.3
- cachetools==5.3.2
- requests==2.31.0

**Note:** All dependencies are installed using `--prefer-binary` flag, which downloads precompiled binary wheels whenever available. This significantly speeds up installation (especially for numpy) and avoids the need for compilation tools.

## Manual Virtual Environment

If you prefer to manage the virtual environment manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install batcontrol (if needed)
pip install -e ../bc-git-upstream-main

# Run application
python app.py

# Deactivate when done
deactivate
```

## Troubleshooting

### "batcontrol not found" or Installation Issues

The script automatically tries two methods:
1. **Local source** (if available at `../batcontrol/bc-git-upstream-main`)
2. **GitHub release** (downloads version 0.5.5 wheel file)

If both fail, you have these options:

**Option 1:** Create a symlink to your local batcontrol
```bash
ln -s /path/to/batcontrol ../batcontrol/bc-git-upstream-main
./run_local.sh
```

**Option 2:** Edit `run_local.sh` and change `BATCONTROL_DIR`
```bash
BATCONTROL_DIR="/your/path/to/batcontrol"
```

**Option 3:** Install batcontrol manually
```bash
source venv/bin/activate
# From local source
pip install -e /path/to/batcontrol
# Or from GitHub
wget https://github.com/muexxl/batcontrol/releases/download/0.5.5/batcontrol-0.5.5-py3-none-any.whl
pip install batcontrol-0.5.5-py3-none-any.whl
```

**Option 4:** Install wget or curl if download fails
```bash
# Ubuntu/Debian
sudo apt-get install wget
# or
sudo apt-get install curl
```

### "Python 3 is not installed"

Install Python 3:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip

# macOS
brew install python3

# Fedora
sudo dnf install python3 python3-pip
```

### "Permission denied"

Make scripts executable:
```bash
chmod +x run_local.sh dev.sh
```

### Port 5000 already in use

The application runs on port 5000 by default. To change it, edit `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=8080)  # Changed from 5000
```

### Import errors after setup

Try reinstalling dependencies:
```bash
./dev.sh clean
./dev.sh setup
```

## Development Workflow

### Typical workflow:

1. **Initial setup** (first time only)
   ```bash
   ./run_local.sh
   ```

2. **Start development**
   ```bash
   ./dev.sh start
   ```

3. **Make changes** to code
   - Flask will auto-reload on file changes (in debug mode)
   - Just refresh your browser

4. **Check environment** if issues arise
   ```bash
   ./dev.sh info
   ```

5. **Clean rebuild** if needed
   ```bash
   ./dev.sh clean
   ./dev.sh setup
   ```

### Working with batcontrol changes

If you're developing batcontrol alongside the simulator:

```bash
# After making changes to batcontrol
source venv/bin/activate
cd ../bc-git-upstream-main
pip install -e .
cd -

# Or just restart the server (if installed in editable mode)
./dev.sh start
```

## Environment Variables

You can set these before running the scripts:

```bash
# Custom Python interpreter
PYTHON=/usr/bin/python3.9 ./run_local.sh

# Skip batcontrol installation
SKIP_BATCONTROL=1 ./run_local.sh

# Enable Flask debug mode (edit app.py)
# Change: app.run(host='0.0.0.0', debug=True, port=5000)
```

## Testing the Setup

After running the setup:

1. **Check environment info**
   ```bash
   ./dev.sh info
   ```

2. **Start the server**
   ```bash
   ./dev.sh start
   ```

3. **Open in browser**
   - Navigate to http://localhost:5000
   - Try loading aWATTar data
   - Run a simulation

4. **Check for errors**
   - Watch terminal output for Python errors
   - Check browser console (F12) for JavaScript errors

## Cleanup

To completely remove the virtual environment:

```bash
./dev.sh clean
```

This removes:
- `venv/` directory
- All `__pycache__/` directories
- All `.pyc` files

## Additional Resources

- **Application Documentation**: See `IMPLEMENTATION_SUMMARY.md`
- **Quick Start Guide**: See `QUICKSTART.md`
- **Design Document**: See `fetch-awattar-data.md`
- **Main README**: See `README.md`

## Support

For issues or questions:
1. Check this README
2. Check `IMPLEMENTATION_SUMMARY.md` for API details
3. Inspect terminal output for error messages
4. Use `./dev.sh info` to check environment status
