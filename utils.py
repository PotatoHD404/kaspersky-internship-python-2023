from datetime import datetime
import fnmatch
import os
from zipfile import ZipInfo

import pytz

from dto import SearchFilters

utc = pytz.UTC


def check_file_mask(file_path: str, file_mask: str) -> bool:
    return fnmatch.fnmatch(file_path, file_mask)


def check_size(file_size: int, size: dict) -> bool:
    if size["operator"] == "gt":
        return file_size > size["value"]
    elif size["operator"] == "lt":
        return file_size < size["value"]
    elif size["operator"] == "eq":
        return file_size == size["value"]

    return False


def check_creation_time(file_creation_time: datetime, creation_time: dict) -> bool:
    target_time = datetime.fromisoformat(creation_time["value"]).replace(tzinfo=utc)

    if creation_time["operator"] == "gt":
        return file_creation_time > target_time
    elif creation_time["operator"] == "lt":
        return file_creation_time < target_time
    elif creation_time["operator"] == "eq":
        return file_creation_time == target_time

    return False


def apply_filters(file_path: str, file_content: bytes, filters: SearchFilters, zip_info: ZipInfo | None) -> bool:

    if filters.text is not None:
        try:
            if filters.text not in file_content.decode("utf-8"):
                return False
        except UnicodeDecodeError:
            return False

    if filters.file_mask is not None and not check_file_mask(file_path, filters.file_mask):
        return False
    if zip_info is not None:
        file_size = zip_info.file_size
    else:
        file_size = len(file_content)
    if filters.size is not None and not check_size(file_size, filters.size):
        return False
    if zip_info is not None:
        file_creation_time = datetime(*zip_info.date_time)
    else:
        file_creation_time = datetime.utcfromtimestamp(os.path.getctime(file_path))

    file_creation_time = file_creation_time.replace(tzinfo=utc)
    if filters.creation_time is not None and not check_creation_time(file_creation_time, filters.creation_time):
        return False

    return True
