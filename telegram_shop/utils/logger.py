import logging
import sys

def setup_logging():
    """
    Configures the logging for the application.
    Logs INFO level messages and above to both a file (bot.log) and the console.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Create a stream handler (for console output)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    # Check if handlers have already been added to avoid duplication
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
