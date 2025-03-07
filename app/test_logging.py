import logging
import requests
import time
from logging.handlers import TimedRotatingFileHandler


# comment the lokihandler class for elk stack
LOKI_URL = "http://localhost:3100/loki/api/v1/push"

class LokiHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "streams": [
                {
                    "stream": {"service": "fastapi"},
                    "values": [[str(int(time.time() * 1e9)), log_entry]],
                }
            ]
        }
        try:
            requests.post(LOKI_URL, json=payload)
        except Exception as e:
            print(f"Error sending log to Loki: {e}")

def setup_logging():
    logger = logging.getLogger("fastapi-logs")
    logger.setLevel(logging.INFO)

    # File logging (optional, for local logs)
    handler = TimedRotatingFileHandler(
        "C:\\Users\\Sarth\\OneDrive\\Documents\\video_membership_fastapi\\app\\logs\\fastapi.log",
        when="midnight", interval=1, backupCount=7
    )
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Loki logging
    loki_handler = LokiHandler()
    loki_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(loki_handler)

    return logger
