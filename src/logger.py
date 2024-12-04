import logging
from logging.handlers import RotatingFileHandler

# Setup rotating file, to prevent .log to grow indefinatly
file_handler = RotatingFileHandler(
    "../client.log",                    # Log file path
    maxBytes=5*1024*1024,               # Max size in bytes (5MB)
    backupCount=3                       # Keep max 3 backup files
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        file_handler                    # Rotating file handler
        #logging.StreamHandler()        # Log to terminal
    ]
)

logger = logging.getLogger("Statify")