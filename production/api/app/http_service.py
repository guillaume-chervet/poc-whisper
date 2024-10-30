import atexit

import httpx
from starlette.background import BackgroundTask

class HttpService:
    def __init__(self):
        self.http_async_client = httpx.AsyncClient(verify=False, timeout=60, follow_redirects=True)
        atexit.register(BackgroundTask(self.http_async_client.aclose))

    def post(self, url, data, headers={}):
        return self.http_async_client.post(url, data=data, headers=headers)



def http_service_factory_get():
    http_service = None
    def get():
        if http_service is None:
            http_service = HttpService()
        return http_service
    return get