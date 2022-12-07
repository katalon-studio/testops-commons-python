from _threading_local import local
from copy import copy
from logging import Logger

import jsonpickle

from testops_commons.configuration.configuration import (
    Configuration, TestOpsConfigurationCreator)
from testops_commons.generator.generator import (ReportGenerator,
                                                 TestOpsReportGenerator)
from testops_commons.helper import helper
from testops_commons.model.models import (Execution, Metadata, Status,
                                          TestResult, TestResults, TestSuite,
                                          TestSuites)
from testops_commons.report_storage import ReportStorage
from testops_commons.uploader.uploader import TestOpsReportUploader


class ReportLifecycle:
    report_storage: ReportStorage
    report_generator: ReportGenerator
    current_execution: str
    current_test_result: local
    test_results: list
    test_suites: list

    def __init__(self, is_parallel=False):
        self.logger: Logger = helper.get_logger(__name__)
        config_creator: TestOpsConfigurationCreator = TestOpsConfigurationCreator()
        self.config: Configuration = config_creator.create_configuration()
        self.config.is_parallel = is_parallel
        self.is_parallel = is_parallel
        self.report_storage = ReportStorage()
        self.report_generator = TestOpsReportGenerator(self.config)
        self.report_uploader = TestOpsReportUploader(self.config)
        self.current_test_result = local()
        self.set_current_test_result_uuid()
        self.test_results = []
        self.test_suites = []

    def set_parallel(self, enabled):
        self.is_parallel = enabled
        self.report_generator.set_parallel(enabled)

    def current_test_result_uuid(self) -> str:
        return self.current_test_result.current_test_result_uuid

    def set_current_test_result_uuid(self):
        self.current_test_result.current_test_result_uuid = helper.generate_unique_value()

    def remove_current_test_result_uuid(self):
        self.current_test_result.current_test_result_uuid = None

    def create_testcases(self, test_results: list) -> TestResults:
        return TestResults(test_results)

    def create_testsuites(self, test_suites: list) -> TestSuites:
        return TestSuites(test_suites)

    def start_execution(self):
        self.current_execution = helper.generate_unique_value()
        execution: Execution = Execution()
        execution.start = helper.current_time_millis()
        execution.uuid = self.current_execution
        self.report_storage.put(execution.uuid, execution)

    def start_suite(self, testsuite: TestSuite, uuid: str):
        testsuite.uuid = uuid
        testsuite.start = helper.current_time_millis()
        execution: Execution = self.report_storage.get(self.current_execution, Execution)
        if execution is not None:
            testsuite.parentUuid = execution.uuid
        self.report_storage.put(uuid, testsuite)

    def start_testcase(self):
        result: TestResult = TestResult()
        result.uuid = self.current_test_result_uuid()
        result.start = helper.current_time_millis()
        self.report_storage.put(result.uuid, result)

    def stop_testcase(self, test_result: TestResult):
        running_testcase: TestResult = self.report_storage.get(self.current_test_result_uuid(), TestResult)
        if running_testcase is not None:
            if test_result.start is None:
                test_result.start = running_testcase.start
            if test_result.stop is None:
                test_result.stop = helper.current_time_millis()
            if test_result.duration is None:
                test_result.duration = test_result.stop - test_result.start
            self.report_storage.remove(self.current_test_result_uuid())
            self.remove_current_test_result_uuid()
        test_result.thread = helper.current_thread_name()
        test_result.host = helper.host_name()
        self.test_results.append(test_result)

    def stop_test_suite(self, uuid: str):
        suite: TestSuite = self.report_storage.get(uuid, TestSuite)
        if suite is not None:
            suite.stop = helper.current_time_millis()
            suite.duration = suite.stop - suite.start
            suite.thread = helper.current_thread_name()
            suite.host = helper.host_name()
            self.report_storage.put(uuid, suite)
            self.test_suites.append(suite)

    def stop_execution(self):
        execution: Execution = self.report_storage.get(self.current_execution, Execution)
        if execution is not None:
            execution.stop = helper.current_time_millis()
            execution.duration = execution.stop - execution.start
            execution.thread = helper.current_thread_name()
            execution.host = helper.host_name()
            execution.status = get_execution_status(self.test_results)
            self.report_storage.put(execution.uuid, execution)

    def write_execution_report(self):
        execution: Execution = self.report_storage.get(self.current_execution, Execution)
        if execution is not None:
            self.report_generator.write_execution(execution)
        self.report_storage.remove(self.current_execution)

    def write_test_suites_report(self):
        self.report_generator.write_test_suites(self.create_testsuites(self.test_suites))

    def write_test_results_report(self):
        self.report_generator.write_test_results(self.create_testcases(self.test_results))

    def write_metadata(self, metadata: Metadata):
        self.report_generator.write_metadata(metadata)

    def write_global_execution_uuid(self, uuid):
        self.report_generator.write_global_execution_uuid(uuid)

    def upload(self):
        self.logger.info("TestOps Configuration:")
        self.logger.info(jsonpickle.encode(_get_config_for_log(self.config), unpicklable=False))
        self.report_uploader.upload()

    def reset(self, clean_report=False):
        self.current_execution = None
        self.report_storage.clear()
        self.test_results.clear()
        self.test_suites.clear()
        self.test_results = None
        self.test_suites = None
        if clean_report:
            self.report_generator.clean_report_dir()


def _get_config_for_log(config):
    config_copy = copy(config)
    config_copy.api_key = "*"
    config_copy.__dict__.pop("is_parallel")
    config_copy.report_folder = config_copy.report_folder.name
    return config_copy


def _get_config_for_log(config):
    config_copy = copy(config)
    config_copy.api_key = "*"
    config_copy.__dict__.pop("is_parallel")
    config_copy.report_folder = config_copy.report_folder.name
    return config_copy


def get_execution_status(test_results: list) -> str:
    for result in test_results:
        if result.status == Status.FAILED:
            return Status.FAILED
    return Status.PASSED
