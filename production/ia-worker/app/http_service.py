import atexit

import httpx
from starlette.background import BackgroundTask

class HttpService:
    def __init__(self):
        self.http_async_client = httpx.AsyncClient(verify=False, timeout=60, follow_redirects=True)
        atexit.register(BackgroundTask(self.http_async_client.aclose))

    def get_http_async_client(self):
        return self.http_async_client

    def post(self, url, data, headers={}):
        return self.http_async_client.post(url, data=data, headers=headers)

http_service_instance = None

def http_service_factory_get():
    global http_service_instance
    if http_service_instance is not None:
        return http_service_instance
    http_service_instance = HttpService()
    return http_service_instance