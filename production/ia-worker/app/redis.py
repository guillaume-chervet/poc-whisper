import redis

class Redis:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=host, port=port, retry_on_timeout=True, decode_responses=True)

    def set_key(self, key:str, data:any):
        self.client.set(key, data)
        self.client.expire(key, 60*10)


    def get_key(self, key:str) -> any:
        return self.client.get(key)
