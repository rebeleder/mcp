import os
import logging
from functools import wraps
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """认证错误"""
    pass

def require_auth(func):
    """
    认证装饰器 - 检查API Key
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 获取API Key - 优先从参数获取，其次从环境变量
        api_key = kwargs.pop('api_key', None)
        expected_key = os.getenv('MCP_API_KEY')

        # 如果没有设置API Key环境变量，跳过认证（开发模式）
        if not expected_key:
            logger.warning("MCP_API_KEY not set, skipping authentication")
            return await func(*args, **kwargs)

        # 验证API Key
        if not api_key or api_key != expected_key:
            logger.warning(f"Authentication failed with key: {api_key}")
            raise AuthenticationError("Invalid API Key. Please provide a valid api_key parameter.")

        logger.info("Authentication successful")
        return await func(*args, **kwargs)
    return wrapper

def require_api_key_or_token(func):
    """
    灵活的认证装饰器 - 支持API Key或JWT Token
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 保存原始参数，因为kwargs会被修改
        original_kwargs = kwargs.copy()

        # 获取认证信息
        api_key = kwargs.pop('api_key', None)
        token = kwargs.pop('token', None)

        expected_key = os.getenv('MCP_API_KEY')
        jwt_secret = os.getenv('JWT_SECRET')

        # 如果没有设置认证环境变量，跳过认证（开发模式）
        if not expected_key and not jwt_secret:
            logger.warning("No authentication configured, skipping authentication")
            return await func(*args, **kwargs)

        # 验证API Key
        if expected_key and api_key:
            if api_key == expected_key:
                logger.info("API Key authentication successful")
                return await func(*args, **kwargs)
            else:
                logger.warning(f"API Key authentication failed")
                raise AuthenticationError("Invalid API Key")

        # 验证JWT Token
        if jwt_secret and token:
            try:
                import jwt
                payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
                logger.info(f"JWT authentication successful for user: {payload.get('sub', 'unknown')}")
                return await func(*args, **kwargs)
            except jwt.InvalidTokenError as e:
                logger.warning(f"JWT authentication failed: {e}")
                raise AuthenticationError("Invalid JWT Token")
            except ImportError:
                logger.error("PyJWT not installed, cannot use JWT authentication")
                raise AuthenticationError("JWT authentication not available")

        # 没有提供认证信息
        raise AuthenticationError("Authentication required. Provide api_key or token parameter.")
    return wrapper

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
                raise AuthenticationError(f"Rate limit exceeded for {identifier}. Please try again later.")

            return await func(*args, **kwargs)
        return wrapper
    return decorator