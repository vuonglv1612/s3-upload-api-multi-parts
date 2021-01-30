import logging
import time

logger = logging.getLogger("uvicorn.error")


def create_temp_filename(filename: str) -> str:
    return f"/tmp/{time.time()}-{filename}"