
import time
from functools import lru_cache


class InstanceMethodCache:

    """
    实例方法缓存 会忽略self参数 函数必须与实例变量无关 否者在并发时可能出错
    """

    def __init__(self, time, *args, **kwargs):
        self.time = time

    def __call__(self, func, *args, **kwargs):
        this = self

        def inner(self, *args, **kwargs):
            this.self = self
            tag = int(time.time())//this.time
            return this._cache(tag, func, *args, **kwargs)
        return inner

    @lru_cache(maxsize=64)
    def _cache(self, tag, func, *args, **kwargs):
        return func(self.self, *args, **kwargs)


