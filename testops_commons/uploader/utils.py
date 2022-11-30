import testops_api
from testops_api import ApiClient
from urllib3 import make_headers, HTTPConnectionPool, HTTPSConnectionPool


PROXY_PROTOCOL_HTTP = "http"

PROXY_PROTOCOL_HTTPS = "https"

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
