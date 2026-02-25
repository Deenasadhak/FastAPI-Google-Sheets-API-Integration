# File: app/core/logging_config.py
import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Log format: timestamp, level, message
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # Propagate to root logger can be set to False if you want to avoid duplicate logs in some setups
        logger.propagate = False

    return logger
