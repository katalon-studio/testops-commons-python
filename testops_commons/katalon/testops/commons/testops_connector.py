import os

import urllib3
from testops_api import ApiClient
from testops_api.api.file_api import FileApi
from testops_api.api.test_report_api import TestReportApi
from testops_api.model.file_resource import FileResource
from testops_api.model.upload_batch_file_resource import UploadBatchFileResource
from urllib3 import PoolManager


class TestOpsConnector:
    api_client: ApiClient

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_upload_urls(self, project_id: int, num_of_urls: int) -> list:
        fa: FileApi = FileApi(self.api_client)
        # print(project_id, number_of_)
        return fa.get_upload_urls(project_id, num_of_urls)

    def upload_testops_report(self, body: list, project_id: int, batch: str) -> None:
        api: TestReportApi = TestReportApi(self.api_client)
        api.process_test_ops_reports(project_id, batch, body)

    def upload_file(self, url: str, file: str):
        with open(file, 'rb') as f:
            http: PoolManager = PoolManager()
            http.request('PUT', url, {
                'filefield': (os.path.basename(file), f.read(), 'application/json'),
            })

