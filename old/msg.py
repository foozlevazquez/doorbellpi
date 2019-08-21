
class AbstractExchange():

    @classmethod
    def init(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def publish(cls, message):
        raise NotImplementedError

    @classmethod
    def receive(cls):
        raise NotImplementedError
