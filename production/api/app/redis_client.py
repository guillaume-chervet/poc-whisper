import redis

class RedisClient:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=host, port=port)

    def set_key(self, key:str, data:any):
        self.client.set(key, data)
        self.client.expire(key, 60*2)


    def get_key(self, key:str) -> any:
        return self.client.get(key)


redis_client_instance = None
def redis_factory_get(host:str, port:int):
    global redis_client_instance
    if redis_client_instance is not None:
        return redis_client_instance
    redis_client_instance = RedisClient(host, port)
    return redis_client_instance

