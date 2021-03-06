import logging
import re
import uuid

from src.exceptions.common import IllegalNameException

logger = logging.getLogger("BLE")
logger.setLevel(logging.DEBUG)


def create_temp_filename(filename: str) -> str:
    return f"/tmp/{uuid.uuid4().hex}-{filename}"


def is_valid_filename(filename: str) -> bool:
    path_matcher = re.compile(r"^[\\ A-Za-z0-9/._:-]*$")
    if path_matcher.match(filename) is None:
        return False
    return True


def nomalize_file_name(filename: str) -> str:
    if not is_valid_filename(filename):
        raise IllegalNameException(name=filename)

    filename = re.sub(r"/+/", "/", filename)
    if filename[0] == "/":
        filename = filename[1:]

    if filename[-1] == "/":
        filename = filename[:-1]
    return filename
