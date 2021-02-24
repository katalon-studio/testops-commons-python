import json
import platform
import socket
import threading
import os
from collections import abc
from os import path
from time import time_ns
from uuid import uuid4

from testops_commons.katalon.testops.commons.model import models

CONFIG_FILE = 'testops-config.json'


def generate_unique_value() -> str:
    return str(uuid4())


def generate_upload_batch() -> str:
    return '{}-{}'.format(generate_unique_value(), current_time_millis())


def is_blank(string: str) -> bool:
    return not string or not string.strip()


def current_time_millis() -> int:
    return time_ns() // 1_000_000


def current_thread_name() -> str:
    return '{}.{}({})'.format(platform.node(), threading.current_thread().name, threading.current_thread().ident)


def host_name() -> str:
    return str(socket.gethostname())


def read_json(file):
    with open(file, 'r', encoding='utf-8') as fp:
        return json.load(fp)


class FrozenJSON:
    def __init__(self, mapping):
        self.__data = dict(mapping)

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)

        if name in self.__data:
            return FrozenJSON.build(self.__data[name])

        return None

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj

    def __repr__(self) -> str:
        return '%r' % self.__data

    def __str__(self) -> str:
        return str(self.__data)


class ConfigRepository:

    def __init__(self):
        self.load()

    def load(self):
        json_data = read_json(CONFIG_FILE)
        data = {**json_data, **os.environ}
        self.__data = FrozenJSON(data)

    def __getattr__(self, name: str):
        return getattr(self.__data, name)
