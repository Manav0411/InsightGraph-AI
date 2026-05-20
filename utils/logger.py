import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Centralized logger configuration.
    Provides standardized readable pipeline logs with timestamps.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        
        # Format: [2026-05-20 15:30:00] [retriever] INFO: message
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
