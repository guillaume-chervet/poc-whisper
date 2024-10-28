import atexit

import httpx
from starlette.background import BackgroundTask
from tensorflow.tools.pip_package.setup import headers


class HttpService:
    def __init__(self):
        self.http_async_client = httpx.AsyncClient(verify=False, timeout=60, follow_redirects=True)
        atexit.register(BackgroundTask(self.http_async_client.aclose))

    def post(self, url, data, headers={}):
        return self.http_async_client.post(url, data=data, headers=headers)