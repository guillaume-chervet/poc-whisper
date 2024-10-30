import redis

class RedisClient:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=host, port=port)

    def set_key(self, key:str, data:any):
        self.client.set(key, data)
        self.client.expire(key, 60*10)


    def get_key(self, key:str) -> any:
        return self.client.get(key)



def redis_factory_get(host:str, port:int):
    redis_instance = None

    def get():
        if redis_instance is None:
            redis_instance = RedisClient(host, port)
        return redis_instance

    return get