import os
import json
import logging
import requests
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Create directory if it doesn't exist
LOG_DIRECTORY = os.environ.get('LOG_DIRECTORY', './logs/app')

if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Configure logging
LOG_FILE = os.path.join(LOG_DIRECTORY, 'log.txt')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
# === CONFIGURATION ===
LOG_API_ENDPOINT = os.environ.get('LOG_API_ENDPOINT', )
LOG_TYPE = [str(i).lower() for i in os.environ.get('LOG_TYPE', 'file').split(',')]
LOG_LEVEL = logging.INFO


def get_remote_ip() -> str:
    """Get remote ip."""
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return 'unknown'

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return 'unknown'
    except Exception as e:
        return 'unknown'

    return session_info.request.remote_ip

def get_session_id(page=False) -> str:
    try:
        ctx = get_script_run_ctx()
        if ctx and ctx.session_id:
            return f"{ctx.session_id}-page" if page else ctx.session_id
        return "unknown-session"
    except Exception as e:
        logging.error(f"Error getting session ID: {e}")
        return "unknown-session"

# === Custom JSON Log Formatter ===
class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "ip": get_remote_ip(),
        }
        return json.dumps(log_record)


# === API Log Handler ===
class ApiLogHandler(logging.Handler):
    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url

    def emit(self, record):
        try:
            log_entry = self.format(record)
            headers = {"Content-Type": "application/json"}
            requests.post(self.api_url, data=log_entry, headers=headers, timeout=5)
        except Exception as e:
            print(f"[Logging error] Could not send log to API: {e}")



def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): The name of the logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    json_formatter = JsonLogFormatter()

    if "api" in LOG_TYPE:
        if not LOG_API_ENDPOINT:
            raise ValueError("LOG_API_ENDPOINT is not set. Please set it in the environment variables.")
        else:
            api_handler = ApiLogHandler(LOG_API_ENDPOINT)
            api_handler.setFormatter(json_formatter)
            logger.addHandler(api_handler)

    if "console" in LOG_TYPE:
        # Log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(json_formatter)
        logger.addHandler(console_handler)

    if "file" in LOG_TYPE:
        # log to file
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(json_formatter)  
        logger.addHandler(file_handler)
    return logger
