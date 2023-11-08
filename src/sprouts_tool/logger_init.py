import logging
import logging.config
import os.path
import json
from dotenv import load_dotenv

# Get path to logging configuration file
load_dotenv()


def load_basic_config():
    """
    Load basic configuration for logging.

    This function sets up the basic configuration for logging, 
    including the logging level, file mode, filename, format, and 
    date format.

    Returns:
        None
    """
    logging.basicConfig(
        level=logging.INFO,
        filemode="a",
        filename="app.log",
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_logging_config():
    """
    Configure logging module using `JSON` configuration file.

    If the environment variable `LOG_CONF_PATH` is set, the logging 
    configuration will be loaded from the specified file. Otherwise, 
    `load_basic_config` will be called to load a basic configuration.

    The function also replaces format specifiers in the configuration 
    file with environment variables. For example, the format specifier 
    '${MY_VAR}' will be replaced with the value of the environment
    variable 'MY_VAR'.

    If the configuration file is invalid or cannot be found, the
    function will fall back to a basic configuration that logs messages 
    to a file named 'app.log' in the current working directory.

    Returns:
        None
    """
    try:
        # Get logging configuration file from environment variable LOG_CONF_PATH
        log_conf_fp = os.environ.get("LOG_CONF_PATH", "./config/logging_config.json")
        with open(log_conf_fp, "r", encoding="utf-8") as f:
            config = f.read()
    except FileNotFoundError:
        load_basic_config()
        logger = logging.getLogger(__name__)
        logger.debug(f"Failed to find configuration file at: {log_conf_fp}")
        logger.warning(
            "Logging configuration file not found. Using default configuration."
        )

    # Replace format specifiers with environment variables
    for k, v in os.environ.items():
        config = config.replace("${" + k.upper().strip() + "}", os.environ.get(k, ""))

    # Configure logging
    try:
        logging.config.dictConfig(json.loads(config))
        logger = logging.getLogger(__name__)
        logger.debug(f"Loaded logging configuration file: {log_conf_fp}")
        logger.debug(f"Logging configuration: {config}")
    except json.decoder.JSONDecodeError:
        load_basic_config()
        logger = logging.getLogger(__name__)
        logger.debug(f"Invalid logging configuration file: {log_conf_fp}")
        logger.warning(
            "Logging configuration file is invalid. Using default configuration."
        )


load_logging_config()