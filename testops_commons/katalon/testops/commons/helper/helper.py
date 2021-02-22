import threading
import platform
import socket
from configparser import ConfigParser
from os import path
from time import time_ns
from uuid import uuid4

from testops_commons.katalon.testops.commons.model import models


class ParameterHelper:
    __testops_section: str = 'testops'

    parser: ConfigParser

    def load_properties(self):
        self.parser = ConfigParser()
        self.parser.read(path.join('..', '..', '..', '..', 'resources', 'testops.ini'))
        pass

    def __init__(self):
        self.load_properties()

    def get_parameter(self, key: str) -> str:
        try:
            return self.parser[self.__testops_section][key]
        except KeyError:
            return None


def generate_unique_value() -> str:
    return str(uuid4())


def generate_upload_batch() -> str:
    return generate_unique_value() + '-' + str(current_time_millis())


def is_blank(string: str) -> bool:
    return (string is None) or (len(string.strip()) == 0)


def current_time_millis() -> int:
    return time_ns() // 1_000_000


def current_thread_name() -> str:
    return f'{platform.node()}.{threading.current_thread().name}({threading.current_thread().ident})'


def host_name() -> str:
    return f'{socket.gethostname()}'


def json_serialize(obj: object):
    if isinstance(obj, list) or isinstance(obj, dict):
        return obj
    return obj.__dict__
