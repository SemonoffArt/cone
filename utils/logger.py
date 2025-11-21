"""
Logging configuration for the Cone application
"""
import logging
import sys
import os


def setup_logger(name='cone_app', level=None):
    """Set up logger with console handler"""
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level from parameter, environment variable, or default to INFO
    if level is None:
        level_str = os.environ.get('CONE_LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, level_str, logging.INFO)
    
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        # Update existing handler level
        for handler in logger.handlers:
            handler.setLevel(level)
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
app_logger = setup_logger()