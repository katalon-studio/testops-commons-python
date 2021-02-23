from pathlib import Path

from testops_commons.katalon.testops.commons.core import constants
from testops_commons.katalon.testops.commons.helper.helper import ParameterHelper, is_blank


class Configuration:
    def __init__(self, server_url, api_key, project_id, report_folder, build_label, build_url) -> None:
        self.server_url = server_url
        self.api_key = api_key
        self.project_id = project_id
        self.report_folder = report_folder
        self.build_url = build_url
        self.build_label = build_label


class ConfigurationCreator:

    def create_configuration(self) -> Configuration:
        pass


class TestOpsConfigurationCreator(ConfigurationCreator):

    def create_configuration(self) -> Configuration:
        param_helper = ParameterHelper()
        server_url: str = param_helper.get_parameter(
            constants.TESTOPS_SERVER_URL)
        if is_blank(server_url):
            server_url = constants.TESTOPS_SERVER_URL_DEFAULT

        report_folder_path: str = param_helper.get_parameter(
            constants.TESTOPS_REPORT_DIRECTORY)
        if is_blank(report_folder_path):
            report_folder_path = constants.TESTOPS_REPORT_DIRECTORY_DEFAULT
        report_folder: Path = Path(report_folder_path)

        api_key: str = param_helper.get_parameter(constants.TESTOPS_API_KEY)
        build_label: str = param_helper.get_parameter(
            constants.TESTOPS_BUILD_LABEL)
        build_url: str = param_helper.get_parameter(
            constants.TESTOPS_BUILD_URL)

        pj_id_str: str = param_helper.get_parameter(
            constants.TESTOPS_PROJECT_ID)
        project_id: int = -1
        if pj_id_str is not None:
            project_id = int(pj_id_str)

        return Configuration(server_url, api_key, project_id, report_folder, build_label, build_url)
