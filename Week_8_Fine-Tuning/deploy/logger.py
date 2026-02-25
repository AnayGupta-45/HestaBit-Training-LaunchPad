import logging
import os
import uuid

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "deploy.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

def get_request_id():
    return str(uuid.uuid4())