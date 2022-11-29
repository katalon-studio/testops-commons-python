import json
import logging
from os import path, getenv
from pathlib import Path
import time

import testops_api
from testops_api import ApiClient
from testops_api.model.file_resource import FileResource
from testops_api.model.upload_batch_file_resource import \
    UploadBatchFileResource
from urllib3 import PoolManager, make_headers, HTTPConnectionPool, HTTPSConnectionPool
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from testops_commons.configuration.configuration import \
    Configuration
from testops_commons.core import constants
from testops_commons.helper import file_helper, helper
from testops_commons.model.models import Apis, CheckpointMatchStatus, CheckpointPixel, RequestMethod, TestOpsException, UploadInfo, VisualTestingCheckpointMismatchException, VisualTestingTimeoutException
from testops_commons.testops_connector import TestOpsConnector

PROXY_PROTOCOL_HTTP = "http"

PROXY_PROTOCOL_HTTPS = "https"


class ReportUploader:
    def upload(self):
        pass


class TestOpsReportUploader(ReportUploader):
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        self.report_pattern = constants.REPORT_PATTERN
        self.testops_connector = TestOpsConnector(self.create_api_client())

    def create_api_client(self) -> ApiClient:
        config: testops_api.Configuration = testops_api.Configuration(
            host=self.configuration.server_url,
            username='',
            password=self.configuration.api_key
        )
        config.verify_ssl = False

        if self.configuration.proxy_information.host:
            if self.configuration.proxy_information.protocol == PROXY_PROTOCOL_HTTP:
                config.proxy = HTTPConnectionPool(host=self.configuration.proxy_information.host
                                                  , port=self.configuration.proxy_information.port)
            elif self.configuration.proxy_information.protocol == PROXY_PROTOCOL_HTTPS:
                config.proxy = HTTPSConnectionPool(host=self.configuration.proxy_information.host
                                                   , port=self.configuration.proxy_information.port)
            proxy_user = self.configuration.proxy_information.username
            proxy_pass = self.configuration.proxy_information.password
            if (proxy_user is not None) and (proxy_pass is not None):
                config.proxy_headers = make_headers(proxy_basic_auth="{}:{}"
                                                    .format(self.configuration.proxy_information.username,
                                                            self.configuration.proxy_information.password))

        client: ApiClient = ApiClient(config)
        return client

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
        urllib3.disable_warnings(InsecureRequestWarning) # Suppress SSL warning
        self.timeout = timeout
        self.__wait_time = 5
        
        self.project_id: int = int(getenv(constants.TESTOPS_PROJECT_ID_ENV))
        self.api_key: str = getenv(constants.TESTOPS_API_KEY_ENV)
        self.server: str = getenv(constants.TESTOPS_SERVER_ENV)
        self.session_id: str = getenv(constants.TESTOPS_SESSION_ID_ENV)

        self.__api_headers = helper.get_api_auth_headers(self.api_key)
        self.__http = PoolManager(1, cert_reqs="CERT_NONE")
        self.__logger = logging.getLogger(__name__)


    def __get_upload_info(self) -> UploadInfo:
        try:
            self.__logger.info("Connecting to Katalon TestOps")
            r = self.__http.request(
                RequestMethod.GET,
                self.server + Apis.GET_UPLOAD_URL,
                fields={"projectId": str(self.project_id)},
                headers=self.__api_headers,
            )
            info = json.loads(r.data.decode())
            return UploadInfo(info["path"], info["uploadUrl"])
        except Exception as e:
            self.__logger.error(__name__ + " Error.")
            raise TestOpsException(e)


    def __upload_file_s3(self, upload_url: str, image_path: str, data: bytes) -> None:
        try:
            self.__logger.info("Uploading Checkpoint image %s to Katalon TestOps", image_path)
            self.__http.request(
                RequestMethod.PUT,
                upload_url,
                body=data,
                headers={"Content-Type": "image/*"},
            )
        except Exception as e:
            self.__logger.error("Failed to upload Checkpoint image %s", image_path)
            raise TestOpsException(e)


    def __send_vst_info(self, name: str, path: str) -> int:
        try:
            r = self.__http.request(
                RequestMethod.POST,
                self.server + Apis.UPLOAD_CHECKPOINT,
                body=json.dumps(
                    {
                        "projectId": str(self.project_id),
                        "sessionId": self.session_id,
                        "batch": helper.generate_upload_batch(),
                        "fileName": name,
                        "uploadedPath": path,
                    }
                ),
                headers=self.__api_headers,
            )
            return int(json.loads(r.data.decode())["id"])
        except Exception as e:
            self.__logger.error(__name__ + " Error.")
            raise TestOpsException(e)


    def __get_vst_result(self, checkpoint_id: int) -> CheckpointPixel:
        try:
            r = self.__http.request(
                RequestMethod.POST,
                self.server + Apis.SEARCH,
                body=json.dumps(
                    {
                        "pagination": {"page": 0, "size": 1, "sorts": []},
                        "conditions": [
                            {
                                "key": "checkpointId",
                                "operator": "=",
                                "value": str(checkpoint_id),
                            },
                            {
                                "key": "Project.id",
                                "operator": "=",
                                "value": str(self.project_id),
                            },
                        ],
                        "type": "CheckpointPixel",
                    }
                ),
                headers=self.__api_headers,
            )
            checkpoint_results: list = json.loads(r.data.decode()).get("content", [])
            if len(checkpoint_results) == 0:
                return CheckpointPixel(None, None)

            checkpoint_pixel: dict = checkpoint_results.pop()
            checkpoint: dict = checkpoint_pixel["checkpoint"]
            checkpoint_name = checkpoint["screenshot"]["name"]
            checkpoint_status = checkpoint.get("matchStatus", None)
            return CheckpointPixel(checkpoint_name, checkpoint_status)
        except Exception as e:
            self.__logger.error(__name__ + " Error.")
            raise TestOpsException(e)


    def verify_checkpoint(self, image_path: str) -> None:
        # Request upload url
        upload_info = self.__get_upload_info()

        # Upload file
        with open(image_path, "rb") as f:
            image_data = f.read()
            self.__upload_file_s3(upload_info.upload_url, image_path, image_data)

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

