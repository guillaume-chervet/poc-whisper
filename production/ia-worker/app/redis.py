import redis

class Redis:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=host, port=port)

    def set_key(self, key:str, data:any):
        self.client.set(key, data)
        self.client.expire(key, 60*10)


    def get_key(self, key:str) -> any:
        return self.client.get(key)


redis_instance = None
def redis_factory_get(host:str, port:int):
    global redis_instance
    if redis_instance is None:
        redis_instance = Redis(host, port)
    return redis_instance