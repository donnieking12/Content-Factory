"""
Logging configuration for the AI Content Factory application
"""
import logging
import logging.config
import os
from typing import Dict, Any

from app.core.config import settings


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "verbose",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "verbose",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "verbose",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # root logger
                "level": "INFO",
                "handlers": ["console", "file", "error_file"]
            },
            "app": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app.services.product_discovery": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app.services.video_generation": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app.services.ai_avatar": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app.services.social_media_publisher": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app.services.content_workflow": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "celery_worker": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            }
        }
    }


def setup_logging() -> None:
    """
    Set up logging configuration
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Configure logging
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    
    # Set logging level based on environment
    root_logger = logging.getLogger()
    if settings.ENVIRONMENT == "development":
        root_logger.setLevel(logging.DEBUG)
    elif settings.ENVIRONMENT == "production":
        root_logger.setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.INFO)


# Create a logger instance that can be used throughout the application
logger = logging.getLogger("app")