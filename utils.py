from datetime import datetime
import fnmatch
import os

from dto import SearchFilters


def check_file_mask(file_path: str, file_mask: str) -> bool:
    return fnmatch.fnmatch(file_path, file_mask)


def check_size(file_content: bytes, size: dict) -> bool:
    file_size = len(file_content)

    if size["operator"] == "gt":
        return file_size > size["value"]
    elif size["operator"] == "lt":
        return file_size < size["value"]
    elif size["operator"] == "eq":
        return file_size == size["value"]

    return False


def check_creation_time(file_path: str, creation_time: dict) -> bool:
    file_creation_time = datetime.utcfromtimestamp(os.path.getctime(file_path))
    target_time = datetime.fromisoformat(creation_time["value"])

    if creation_time["operator"] == "gt":
        return file_creation_time > target_time
    elif creation_time["operator"] == "lt":
        return file_creation_time < target_time
    elif creation_time["operator"] == "eq":
        return file_creation_time == target_time

    return False


def apply_filters(file_path: str, file_content: bytes, filters: SearchFilters) -> bool:
    if filters.contains_text is not None:
        try:
            if filters.contains_text not in file_content.decode("utf-8"):
                return False
        except UnicodeDecodeError:
            return False

    if filters.file_mask is not None and not check_file_mask(file_path, filters.file_mask):
        return False

    if filters.size is not None and not check_size(file_content, filters.size):
        return False

    if filters.creation_time is not None and not check_creation_time(file_path, filters.creation_time):
        return False

    return True
