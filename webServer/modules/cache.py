"""
The cache class is an in-memory method of caching data returned from a function

cache takes 2 arguments; getFunction and expiryDelta. getFunction is the function
that you want to be called when you get() from the cache. expiryDelta is the
amount of time that you want the data to be cached for (as a datetime.timedelta
object)

For example, you have a function that performs an API request, and returns JSON
data. Using the cache class you can call get() any amount of time you want, but
the JSON data will only be updated if expiryDelta has passed since the last time
you called cache.get(). This would be so you don't spam the API with requests
"""

from datetime import datetime

class cache(object):
    def __init__(self, getFunction, expiryDelta):
        self.getFunction = getFunction
        self.cacheExpiryDelta = expiryDelta
        self.previousRequestTime = datetime.now() - expiryDelta
    
    def get(self):
        currentTime = datetime.now()
        currentDelta = currentTime - self.previousRequestTime
        if currentDelta >= self.cacheExpiryDelta:
            self.cachedReturn = self.getFunction()
            self.previousRequestTime = currentTime
        return self.cachedReturn
