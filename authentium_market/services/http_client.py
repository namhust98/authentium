import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

RETRIES = 5
TIMEOUT = 60


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class HttpClient():
    def retry_http(self) -> requests.Session:
        retry_strategy = Retry(total=RETRIES, backoff_factor=1)
        adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http
