from pathlib import Path
from datetime import datetime
import logging


PROJECT_ROOT = Path.cwd()

LOG_FILE = f"{datetime.now().strftime('%y_%m_%d_%H_%M_%S')}.log"

LOG_PATH = PROJECT_ROOT / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)

LOG_FILE_PATH = LOG_PATH / LOG_FILE


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(filename)s: %(lineno)d | %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_FILE_PATH), logging.StreamHandler()],
)
