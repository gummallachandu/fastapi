import logging
import sys

# Configure logging
def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add handlers if they don't exist
    if not root_logger.handlers:
        root_logger.addHandler(stream_handler)

def get_logger(name: str):
    """
    Returns a logger instance with the specified name.
    """
    return logging.getLogger(name)

# Initial setup when the module is imported
setup_logging() 