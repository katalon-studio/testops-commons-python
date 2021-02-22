from pathlib import Path

import testops_api
from testops_api import ApiClient
from testops_api.model.file_resource import FileResource
from testops_api.model.upload_batch_file_resource import UploadBatchFileResource

from testops_commons.katalon.testops.commons.configuration.configuration import Configuration
from testops_commons.katalon.testops.commons.core import constants
from testops_commons.katalon.testops.commons.helper import helper, file_helper
from testops_commons.katalon.testops.commons.testops_connector import TestOpsConnector


class ReportUploader:
    def upload(self):
        pass


class TestOpsReportUploader(ReportUploader):
    testops_connector: TestOpsConnector

    configuration: Configuration

    report_pattern: str

    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        self.report_pattern = constants.REPORT_PATTERN
        self.testops_connector = TestOpsConnector(self.create_api_client())

    def create_api_client(self) -> ApiClient:
        config: testops_api.Configuration = testops_api.Configuration(host=self.configuration.build_url,
                                                                      api_key=self.configuration.api_key)
        client: ApiClient = ApiClient(config)
        return client

    def upload_file(self, info: FileResource, file_path: str, is_end: bool) -> UploadBatchFileResource:
        file_resource: UploadBatchFileResource = UploadBatchFileResource()
        path: Path = Path(file_path)
        try:
            self.testops_connector.upload_file(info.get('upload_url'), path.absolute())
            file_resource.set_attribute('file_name', path.name)
            file_resource.set_attribute('folder_path', path.parent.absolute())
            file_resource.set_attribute('uploaded_path', info.get('uploaded_path'))
            file_resource.set_attribute('end', is_end)
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
        file_resources: list = self.testops_connector.get_upload_urls(project_id, len(files))
        bath: str = helper.generate_upload_batch()
        uploaded: list = []
        for i in range(0, len(files) - 1):
            is_end: bool = i == len(files) - 1
            rel = self.upload_file(file_resources[i], files[i], is_end)
            if rel is not None:
                uploaded.append(rel)
        self.testops_connector.upload_testops_report(uploaded, project_id, bath)
