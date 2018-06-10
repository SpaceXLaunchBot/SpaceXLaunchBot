"""
A subclass of StrictRedis that deals with errors from Redis
---
There is a file like this being used by the bot, but the one the bot uses
cannot be used here as this is the synchronous version of the library, as
supposed to the async version, which needs an async loop to work
"""

from redis import StrictRedis
import pickle

class redisClient(StrictRedis):
    def __init__(self, unix_socket_path, db=0):
        super().__init__(unix_socket_path=unix_socket_path, db=db)

    def safeGet(self, key, serialized=False):
        try:
            if serialized:
                return pickle.loads(self.get(key))
            return self.get(key)
        except Exception as e:
            return 0

    def safeSet(self, key, value, serialize=False):
        try:
            if serialize:
                return self.set(key, pickle.dumps(value))
            return self.set(key, value)
        except Exception as e:
            return 0
