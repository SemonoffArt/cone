"""
Logging configuration for the Cone application
"""
import logging
import sys
import os
from pathlib import Path
from utils.constants import LOG_LEVEL


def setup_logger(name='cone_app', level=None, log_to='console', log_file='cone_app.log'):
    """
    Set up logger with console and/or file handler
    
    Args:
        name: Logger name
        level: Logging level - can be string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') or logging level object
        log_to: Where to output logs - 'console', 'file', or 'both'
        log_file: Path to log file (only used if log_to is 'file' or 'both')
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level from parameter, environment variable, or default to INFO
    if level is None:
        level_str = os.environ.get('CONE_LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, level_str, logging.INFO)
    elif isinstance(level, str):
        # Convert string to logging level
        level_str = level.upper()
        level = getattr(logging, level_str, logging.INFO)
    # else: level is already a logging level object
    
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        # Update existing handler level
        for handler in logger.handlers:
            handler.setLevel(level)
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get log_to preference from environment variable if not specified
    if log_to == 'console':
        log_to = os.environ.get('CONE_LOG_TO', 'console').lower()
    
    # Add console handler if needed
    if log_to in ['console', 'both']:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if needed
    if log_to in ['file', 'both']:
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path('logs')
            logs_dir.mkdir(exist_ok=True)
            
            log_file_path = logs_dir / log_file
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")
    
    return logger


# Create default logger instance
# Use environment variables or defaults
app_logger = setup_logger(log_to='both', level=LOG_LEVEL)