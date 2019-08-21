import redis

from msg import AbstractExchange

class RedisExchange(AbstractExchange):

    redis = None

    @classmethod
    def init(cls, **kwargs):
        cls.redis =

    @classmethod
    def publish(cls, message):
        raise NotImplementedError

    @classmethod
    def receive(cls):
        raise NotImplementedError
