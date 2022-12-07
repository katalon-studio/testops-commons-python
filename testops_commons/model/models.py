from dataclasses import dataclass


STRING_EMPTY: str = ''


class Error:
    def __init__(self, message: str = None, stack_trace: str = None):
        self.message = message
        self.stackTrace = stack_trace


class Status:
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCOMPLETE = "INCOMPLETE"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class Execution:
    def __init__(self, uuid: str = None, parent_uuid: str = None, status: str = None, start: int = None,
                 stop: int = None, duration: int = None, thread: str = None, host: str = None):
        self.uuid: str = uuid
        self.parentUuid: str = parent_uuid
        self.status: str = status
        self.start: int = start
        self.stop: int = stop
        self.duration: int = duration
        self.thread: str = thread
        self.host: str = host


class TestSuite:
    def __init__(self, uuid: str = None, parent_uuid: str = None, name: str = None, description: str = None,
                 status: str = None, start: int = None, stop: int = None, duration: int = None, thread: str = None,
                 host: str = None):
        self.uuid: str = uuid
        self.parentUuid: str = parent_uuid
        self.name: str = name
        self.description: str = description
        self.status: str = status
        self.start: int = start
        self.stop: int = stop
        self.duration: int = duration
        self.thread: str = thread
        self.host: str = host


class TestResult:
    def __init__(self, uuid: str = None, parent_uuid: str = None, name: str = None, suite_name: str = None,
                 description: str = None, parameters: dict = None, status: str = None, errors: list = None,
                 start: int = None, stop: int = None, duration: int = None, thread: str = None, host: str = None):
        self.uuid: str = uuid
        self.parentUuid: str = parent_uuid
        self.name: str = name
        self.suiteName: str = suite_name
        self.description: str = description
        self.parameters: dict = parameters
        self.status: str = status
        self.errors: list = errors
        self.start: int = start
        self.stop: int = stop
        self.duration: int = duration
        self.thread: str = thread
        self.host: str = host
        if self.parameters is None:
            self.parameters = {}
        if self.errors is None:
            self.errors = []


class Metadata:
    def __init__(self, framework: str, language: str, version: str, build_label: str, build_url: str) -> None:
        self.framework = framework
        self.language = language
        self.version = version
        self.buildLabel = build_label
        self.buildUrl = build_url


class TestSuites:
    def __init__(self, test_suites: list):
        self.suites = test_suites


class TestResults:
    def __init__(self, test_results: list):
        self.results = test_results

class TestOpsException(Exception):
    ...

class VisualTestingCheckpointMismatchException(TestOpsException):
    ...

class VisualTestingTimeoutException(TestOpsException):
    ...

@dataclass
class RequestMethod:
    GET: str = "GET"
    POST: str = "POST"
    PUT: str = "PUT"


@dataclass
class Apis:
    GET_UPLOAD_URL: str = "/api/v1/files/upload-url"
    UPLOAD_CHECKPOINT: str = "/api/v1/checkpoints"
    SEARCH: str = "/api/v1/search"
    UPDATE_RUNNING_TEST_RUN: str = '/api/v1/katalon/test-reports/update-result?projectId={project_id}'


@dataclass
class CheckpointMatchStatus:
    NEW = "NEW"
    MISMATCH = "MISMATCH"
    MATCH = "MATCH"
    MISSING = "MISSING"

class UploadInfo:
    def __init__(self, path: str, upload_url) -> None:
        self.path = path
        self.upload_url = upload_url


class CheckpointPixel:
    def __init__(self, name: str, matchStatus: str) -> None:
        self.name = name
        self.matchStatus = matchStatus
