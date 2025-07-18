import redis


class RedisCacheManager:
    def __init__(self, host='localhost', port=6379, db=0, protocol=3):
        self.client = redis.Redis(host=host, port=port, db=db, protocol=protocol)

    def ready(self):
        try:
            self.client.ping()
            return True
        except redis.exceptions.ConnectionError:
            return False

    def get(self, key):
        try:
            return self.client.get(key).decode('utf-8')
        except Exception as e:
            return None

    def set(self, key, value, time=3600):
        if key in self.client:
            self.client.delete(key)
        if time is None:
            self.client.set(key, value)
        self.client.set(key, value, ex=time)

    def expire(self, key, time):
        self.client.expire(key, time)

    def delete(self, key):
        self.client.delete(key)
