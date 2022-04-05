import logging

from datetime import datetime
from pytz import timezone

def remove_ext(file_name: str) -> str:
    idx = file_name.rfind(".")
    if idx == -1:
        return file_name
    return file_name[:idx]


def _get_current_log_time() -> str:
    return datetime.now(timezone('Asia/Seoul')).strftime("%y.%m.%d %H:%M:%S")


def log_info(msg: str) -> None:
    current_time = _get_current_log_time()
    logging.info(f"[{current_time}] {msg}")


def log_wanring(msg: str) -> None:
    current_time = _get_current_log_time()
    logging.warning(f"[{current_time}] {msg}")


