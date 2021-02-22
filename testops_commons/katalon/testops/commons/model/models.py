from enum import Enum

STRING_EMPTY: str = ''


class Error:
    message: str = None
    stack_trace: str = None

    def __init__(self, message: str, stack_trace: str):
        self.message = message
        self.stack_trace = stack_trace


class Status(Enum):
    PASSED = 0
    FAILED = 1
    INCOMPLETE = 2
    ERROR = 3
    SKIPPED = 4


class Execution:
    uuid: str = None
    parent_uuid: str = None
    status: str = None
    start: int = None
    stop: int = None
    duration: int = None
    thread: str = None
    host: str = None


class TestSuite:
    uuid: str = None
    parent_uuid: str = None
    name: str = None
    description: str = None
    status: str = None
    start: int = None
    stop: int = None
    duration: int = None
    thread: str = None
    host: str = None


class TestResult:
    uuid: str = None
    parent_uuid: str = None
    name: str = None
    suite_name: str = None
    description: str = None
    parameters: dict = {}
    status: str = None
    errors: list = []
    start: int = None
    stop: int = None
    duration: int = None
    thread: str = None
    host: str = None


class Metadata:
    def __init__(self, framework: str, language: str, version: str, build_label: str, build_url: str) -> None:
        self.framework = framework
        self.language = language
        self.version = version
        self.build_label = build_label
        self.build_url = build_url

    framework: str = None
    language: str = None
    version: str = None
    build_label: str = None
    build_url: str = None


class TestSuites:
    suites: list = []

    def __init__(self, test_suites: list):
        self.suites = test_suites


class TestResults:
    results: list = []

    def __init__(self, test_results: list):
        self.results = test_results
