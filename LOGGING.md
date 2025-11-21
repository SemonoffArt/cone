# Logging in Cone Application

## Overview

The Cone application uses Python's built-in logging module to provide console output for debugging and monitoring application behavior.

## Logger Configuration

The logger is configured in `utils/logger.py` and provides:

1. Console output formatting with timestamps
2. Configurable log levels via environment variables
3. Reusable logger instances across modules

## Usage

### Basic Usage

```python
from utils.logger import app_logger

# Info level messages
app_logger.info("Application started")

# Warning level messages
app_logger.warning("This is a warning")

# Error level messages
app_logger.error("An error occurred")

# Debug level messages (only shown when log level is DEBUG)
app_logger.debug("Debug information")
```

### Creating Custom Loggers

```python
from utils.logger import setup_logger
import logging

# Create a custom logger with a specific name
custom_logger = setup_logger('my_custom_logger')

# Create a custom logger with a specific level
debug_logger = setup_logger('debug_logger', logging.DEBUG)
```

### Setting Log Level

The log level can be controlled through the `CONE_LOG_LEVEL` environment variable:

- `DEBUG` - Show all messages
- `INFO` - Show info, warning, and error messages (default)
- `WARNING` - Show only warning and error messages
- `ERROR` - Show only error messages

Example (Windows PowerShell):
```powershell
$env:CONE_LOG_LEVEL="DEBUG"
python main.py
```

Example (Linux/Mac):
```bash
export CONE_LOG_LEVEL=DEBUG
python main.py
```

## Log Format

Logs are displayed in the following format:
```
[timestamp] - [logger name] - [level] - [message]
```

Example:
```
2025-11-20 20:27:27,378 - cone_app - INFO - Application started
```

## Integration

The logger is integrated into various components of the application:

- Main application window
- Configuration management
- Triangle calculations
- Cone volume calculations
- UI components

All major operations and errors are logged for debugging purposes.