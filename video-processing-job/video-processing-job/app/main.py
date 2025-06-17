# Configure logging for Cloud Run. Logs will appear in Cloud Logging.
import sys, logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # Direct logs to stdout for Cloud Run to capture
    ]
)

from .bucket import * 