import logging
import sys
from pathlib import Path

def setup_logger():
    """Sets up a project-wide logger that writes to console and a log file."""
    
    # Define the directory for logs
    log_dir = Path(__file__).parent.parent / "reports"
    log_dir.mkdir(exist_ok=True) # Ensures the root directory
    log_file = log_dir / "audit_run.log"

    
    logger = logging.getLogger()
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.setLevel(logging.INFO) 

    # Create a formatter - this defines the structure of the log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    # Create a handler to write to the log file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger