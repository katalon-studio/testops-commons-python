from pathlib import Path

from testops_commons.katalon.testops.commons.core.constants import *
from testops_commons.katalon.testops.commons.helper.helper import ConfigRepository, is_blank


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
        config = ConfigRepository()
        server_url: str = config.get_config(
            TESTOPS_SERVER_URL,
            env_name=TESTOPS_SERVER_URL_ENV,
            default=TESTOPS_SERVER_URL_DEFAULT)

        report_folder_path: str = config.get_config(
            TESTOPS_REPORT_FOLDER,
            env_name=TESTOPS_REPORT_FOLDER_ENV,
            default=TESTOPS_REPORT_FOLDER_DEFAULT)
        report_folder: Path = Path(report_folder_path)

        api_key: str = config.get_config(
            TESTOPS_API_KEY,
            env_name=TESTOPS_API_KEY_ENV)
        build_label: str = config.get_config(
            TESTOPS_BUILD_LABEL,
            env_name=TESTOPS_BUILD_LABEL_ENV)
        build_url: str = config.get_config(
            TESTOPS_BUILD_URL,
            env_name=TESTOPS_BUILD_URL_ENV)
        pj_id_str: str = config.get_config(
            TESTOPS_PROJECT_ID,
            env_name=TESTOPS_PROJECT_ID_ENV)
        project_id: int = -1
        if pj_id_str is not None:
            project_id = int(pj_id_str)

        return Configuration(server_url, api_key, project_id, report_folder, build_label, build_url)
