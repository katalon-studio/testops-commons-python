import requests
from testops_api import ApiClient
from testops_api.api.file_api import FileApi
from testops_api.api.test_report_api import TestReportApi
from testops_api.api.visual_testing_api import VisualTestingApi
from testops_api.model.checkpoint_resource import CheckpointResource
from testops_api.model.search_request import SearchRequest
from testops_api.model.search_request_condition import SearchRequestCondition
from testops_api.model.search_request_pagination import SearchRequestPagination
from testops_api.api.search_api import SearchApi

class TestOpsConnector:

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_upload_urls(self, project_id: int, num_of_urls: int) -> list:
        fa = FileApi(self.api_client)
        return fa.get_upload_urls(project_id, num_of_urls)

    def upload_testops_report(self, body: list, project_id: int, batch: str) -> None:
        api = TestReportApi(self.api_client)
        api.process_test_ops_reports(project_id, batch, body)

    def upload_file(self, url: str, file: str):
        with open(file, 'rb') as f:
            return requests.put(url, data=f)

    def get_upload_url(self, project_id: int):
        api = FileApi(self.api_client)
        return api.get_upload_url(project_id)

    def upload_checkpoint(self, body) -> CheckpointResource:
        api = VisualTestingApi(self.api_client)
        return api.upload_checkpoint(body)

    def get_checkpoint_pixel_by_checkpoint_id(self, checkpoint_id):
        api = VisualTestingApi(self.api_client)
        return api.get_checkpoint_pixel_by_checkpoint_id(checkpoint_id)
