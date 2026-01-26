"""Application with complete observability."""

import logging
import time
from logging.config import fileConfig

# Configure logging
fileConfig("logging.conf")
logger = logging.getLogger(__name__)


def get_health():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": time.time()}


def process_request(data):
    """Process request with timing and error handling."""
    start_time = time.time()
    try:
        if not data:
            raise ValueError("Data cannot be empty")
        logger.info(f"Processing request with {len(data)} items")
        result = sum(data)
        duration = time.time() - start_time
        logger.info(f"Request processed in {duration:.3f}s")
        return result
    except ValueError as e:
        logger.exception(f"Error processing request: {str(e)}")
        raise
