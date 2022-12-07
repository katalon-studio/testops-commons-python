import logging
from os import path, getenv
from pathlib import Path
import time

from testops_api.model.file_resource import FileResource
from testops_api.model.upload_batch_file_resource import \
    UploadBatchFileResource
from testops_api.model.upload_checkpoint_resource import UploadCheckpointResource

from testops_commons.configuration.configuration import \
    Configuration, TestOpsConfigurationCreator
from testops_commons.core import constants
from testops_commons.helper import file_helper, helper
from testops_commons.model.models import Apis, CheckpointMatchStatus, CheckpointPixel, RequestMethod, TestOpsException, UploadInfo, VisualTestingCheckpointMismatchException, VisualTestingTimeoutException
from testops_commons.testops_connector import TestOpsConnector
from .utils import create_api_client

PROXY_PROTOCOL_HTTP = "http"

PROXY_PROTOCOL_HTTPS = "https"


class ReportUploader:
    def upload(self):
        pass


class TestOpsReportUploader(ReportUploader):
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        self.report_pattern = constants.REPORT_PATTERN
        self.testops_connector = TestOpsConnector(create_api_client(self))

    def upload_file(self, info: FileResource, file_path: str, is_end: bool) -> UploadBatchFileResource:
        file_resource: UploadBatchFileResource = UploadBatchFileResource()
        file_path_absolute = path.realpath(file_path)
        parent_path_absolute = path.dirname(file_path_absolute)
        file_name = path.basename(file_path)
        try:
            self.testops_connector.upload_file(
                info.upload_url, file_path_absolute)
            file_resource.file_name = file_name
            file_resource.folder_path = parent_path_absolute
            file_resource.uploaded_path = info.path
            file_resource.end = is_end
            return file_resource
        except Exception as e:
            return None

    def upload(self):
        api_key = self.configuration.api_key
        if helper.is_blank(api_key):
            return

        project_id = self.configuration.project_id
        if project_id is None:
            return

        report_path: Path = self.configuration.report_folder
        files: list = file_helper.scan_files(report_path)
        file_resources: list = self.testops_connector.get_upload_urls(
            project_id, len(files))
        bath: str = helper.generate_upload_batch()
        uploaded = []
        for i, (file, file_resource) in enumerate(zip(files, file_resources)):
            is_end = i == len(files) - 1
            rel = self.upload_file(file_resource, file, is_end)
            if rel:
                uploaded.append(rel)
        self.testops_connector.upload_testops_report(
            uploaded, project_id, bath)


class VisualTestingUploader:
    
    def __init__(self, timeout: int = 60) -> None:
        self.report_pattern = constants.REPORT_PATTERN
        self.__logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.__wait_time = 5

        self.session_id: str = getenv(constants.TESTOPS_SESSION_ID_ENV)

        testOpsConfigurationCreator: TestOpsConfigurationCreator = TestOpsConfigurationCreator()
        self.configuration: Configuration = testOpsConfigurationCreator.create_configuration()
        
        self.testops_connector = TestOpsConnector(create_api_client(self))
        
        

    def __get_upload_info(self) -> FileResource:
        api_key = self.configuration.api_key
        if helper.is_blank(api_key):
            return None

        project_id = self.configuration.project_id
        if project_id is None:
            return None
        try:
            self.__logger.info("Connecting to Katalon TestOps")
            return self.testops_connector.get_upload_url(project_id=project_id)
        except Exception as e:
            self.__logger.error(__name__ + " Error.")
            raise TestOpsException(e)


    def __send_vst_info(self, name: str, path: str) -> int:
        try:
            upload_checkpoint_resource: UploadCheckpointResource = UploadCheckpointResource()
            upload_checkpoint_resource.project_id = self.configuration.project_id
            upload_checkpoint_resource.session_id = self.session_id
            upload_checkpoint_resource.batch = helper.generate_upload_batch()
            upload_checkpoint_resource.file_name = name
            upload_checkpoint_resource.uploaded_path = path
            if self.configuration.baseline_collection_id != -1:
                upload_checkpoint_resource.baseline_collection_id = self.configuration.baseline_collection_id
            return self.testops_connector.upload_checkpoint(upload_checkpoint_resource).id
        except Exception as e:
            self.__logger.error(__name__ + " Error.")
            raise TestOpsException(e)


    def __get_vst_result(self, checkpoint_id: int) -> CheckpointPixel:
        try:
            checkpoint_pixel = self.testops_connector.get_checkpoint_pixel_by_checkpoint_id(checkpoint_id=checkpoint_id)
            if checkpoint_pixel == None:
                return CheckpointPixel(None, None)

            checkpoint: dict = checkpoint_pixel["checkpoint"]
            checkpoint_name = checkpoint["screenshot"]["name"]
            checkpoint_status = checkpoint.get("match_status", None)
            return CheckpointPixel(checkpoint_name, checkpoint_status)
        except Exception as e:
            self.__logger.error(__name__ + " Error.")
            raise TestOpsException(e)


    def verify_checkpoint(self, image_path: str) -> None:
        # Request upload url
        upload_info = self.__get_upload_info()

        # Upload file
        self.testops_connector.upload_file(upload_info.upload_url, image_path)

        checkpoint_name = file_helper.get_file_name(image_path)
        checkpoint_id: int = self.__send_vst_info(checkpoint_name, upload_info.path)

        # Waiting for result
        self.__logger.info("Waiting for Visual Testing result from Katalon TestOps...")
        start_time = time.time()
        while True:
            time.sleep(self.__wait_time)
            checkpoint_result = self.__get_vst_result(checkpoint_id)

            if checkpoint_result.matchStatus == CheckpointMatchStatus.MATCH:
                self.__logger.info("Checkpoint MATCH: " + checkpoint_result.name)
                break
            if checkpoint_result.matchStatus == CheckpointMatchStatus.MISMATCH:
                raise VisualTestingCheckpointMismatchException("Checkpoint MISMATCH: " + checkpoint_result.name)

            if checkpoint_result.matchStatus == CheckpointMatchStatus.NEW:
                self.__logger.info("New Checkpoint: " + checkpoint_result.name)
                break

            if (time.time() - start_time) > self.timeout:
                raise VisualTestingTimeoutException(
                    "Failed to verify Checkpoint "
                    + checkpoint_name
                    + ". Timeout."
                )

