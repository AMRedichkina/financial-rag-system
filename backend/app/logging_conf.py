import logging
import sys
from logging import Formatter, StreamHandler
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    include_uvicorn: bool = True,
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string. If None, uses default format.
        include_uvicorn: Whether to configure uvicorn access logs (default: True)
    """
    if format_string is None:
        format_string = (
            "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(Formatter(format_string))
    root_logger.addHandler(console_handler)
    
    # Configure third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langgraph").setLevel(logging.INFO)
    
    # Configure uvicorn loggers
    if include_uvicorn:
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.setLevel(logging.INFO)
        
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.setLevel(logging.INFO)
        uvicorn_access.propagate = True
    
    # Set application logger level
    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)
    
    logging.info(f"Logging configured at level: {logging.getLevelName(level)}")
