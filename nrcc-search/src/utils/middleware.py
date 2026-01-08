import logging
from functools import wraps
from typing import Dict

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """速率限制错误"""
    pass


class RateLimiter:
    """
    简单的速率限制器
    """
    def __init__(self, max_calls: int = 100, time_window: int = 3600):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        import time
        now = time.time()

        # 清理过期记录
        if identifier in self.calls:
            self.calls[identifier] = [
                call_time for call_time in self.calls[identifier]
                if now - call_time < self.time_window
            ]

        # 检查是否超过限制
        if identifier not in self.calls:
            self.calls[identifier] = []

        if len(self.calls[identifier]) >= self.max_calls:
            return False

        # 记录本次调用
        self.calls[identifier].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter(max_calls=50, time_window=3600)  # 每小时50次调用


def rate_limit(identifier_func=lambda: "default"):
    """
    速率限制装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            identifier = identifier_func() if callable(identifier_func) else str(identifier_func)

            if not rate_limiter.is_allowed(identifier):
                raise RateLimitError(f"Rate limit exceeded for {identifier}. Please try again later.")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
