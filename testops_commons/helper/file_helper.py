import shutil
from os import walk, path
from pathlib import Path
import re

from testops_commons.core import constants
from os.path import basename


def ensure_directory(directory: Path):
    p = directory
    if isinstance(p, str):
        p = Path(p)
    p.mkdir(parents=True, exist_ok=True)


def scan_files(report_path: Path) -> list:
    paths = []
    __scan_dir(paths, report_path)
    return paths


def clean_dir(path):
    p = path
    if isinstance(p, str):
        p = Path(p)
    shutil.rmtree(p)


def get_file_name(path: str) -> str:
    return basename(path)


def __scan_dir(paths: list, directory: Path):
    for (dir_path, dir_names, file_names) in walk(directory):
        for f in file_names:
            if __is_report_file(f):
                paths.append(path.join(dir_path, f))
        for d in dir_names:
            __scan_dir(paths, d)


def __is_report_file(file: str) -> bool:
    return re.match(constants.REPORT_PATTERN, file, re.IGNORECASE)
