# Installation Guide

## Installing the Package

### Development Installation (Editable Mode)

If you want to develop or modify the package:

```bash
# Navigate to project directory
cd geo-chat-project

# Install in editable mode
pip install -e .

# Or with API dependencies (for FastAPI servers)
pip install -e ".[api]"
```

### Regular Installation

```bash
# From the project directory
pip install .

# Or with API dependencies
pip install ".[api]"
```

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/ohypka/geo-chat-project.git
cd geo-chat-project

# Install
pip install -e .
```

## Usage

### Basic Import

```python
from geo_chat import (
    normalize_environment_data,
    get_doctor_availability,
    get_doctor_coordinates,
)
```

### Environment Variables

Create a `.env` file in your project root:

```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Or set environment variables directly:

```bash
# Windows PowerShell
$env:OPENWEATHER_API_KEY="your_key_here"

# Linux/Mac
export OPENWEATHER_API_KEY="your_key_here"
```

### Example Usage

See `examples/basic_usage.py` for complete examples.

```python
from geo_chat import normalize_environment_data

# Get weather and air quality data
data = normalize_environment_data(
    lat=52.2297,
    lon=21.0122,
    name="Warsaw"
)

print(f"Temperature: {data['metrics']['temperature']}°C")
```

## Building Distribution Packages

### Build Wheel and Source Distribution

```bash
# Install build tools
pip install build

# Build packages
python -m build
```

This will create:
- `dist/geo_chat-0.1.0-py3-none-any.whl` (wheel)
- `dist/geo_chat-0.1.0.tar.gz` (source distribution)

### Publishing to PyPI (when ready)

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

## Project Structure

```
geo-chat-project/
├── geo_chat/              # Main package
│   ├── __init__.py       # Package exports
│   ├── environment/      # Weather & air quality module
│   │   ├── __init__.py
│   │   └── weather.py
│   └── doctors/          # Doctors availability module
│       ├── __init__.py
│       └── availability.py
├── examples/              # Usage examples
├── src/                   # Original source (legacy)
├── pyproject.toml         # Package configuration
├── setup.py               # Setup script (backward compatibility)
└── requirements.txt       # Dependencies
```

## Dependencies

### Core Dependencies
- `requests>=2.32.0` - HTTP requests
- `python-dotenv>=1.2.0` - Environment variable management

### Optional Dependencies (for API servers)
- `fastapi>=0.121.0` - FastAPI framework
- `uvicorn>=0.38.0` - ASGI server
- `pydantic>=2.12.0` - Data validation

Install with:
```bash
pip install -e ".[api]"
```
