# MCP服务器身份验证指南

本文档介绍了如何为NRCC化学品搜索MCP服务器配置和使用身份验证功能。

## 🚀 功能特性

- **多种认证方式**: 支持API Key和JWT Token两种认证方式
- **灵活的认证策略**: 可以同时支持多种认证方式，或选择其中一种
- **速率限制**: 内置速率限制功能，防止API滥用
- **安全日志**: 完整的认证日志记录，便于监控和故障排查

## 🔧 环境配置

### 1. 基础配置

复制环境变量示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
# MCP 服务器配置
MCP_API_KEY=your-secret-api-key-here
JWT_SECRET=your-jwt-secret-key-here

# 速率限制配置（可选）
RATE_LIMIT_MAX_CALLS=50
RATE_LIMIT_WINDOW=3600

# 服务器配置
MCP_HOST=localhost
MCP_PORT=8000
MCP_LOG_LEVEL=INFO
```

### 2. 安装依赖

确保安装了PyJWT：
```bash
pip install pyjwt>=2.8.0
```

## 🔑 认证方式

### API Key 认证

**服务器端配置：**
```env
MCP_API_KEY=your-secret-api-key-here
```

**客户端使用：**
```python
# 方式1: 直接参数传递
result = await get_chemicals_list_tool(
    chemName="滴滴涕",
    chemCas="50-29-3",
    api_key="your-secret-api-key-here"
)

# 方式2: 环境变量（推荐）
import os
os.environ['MCP_API_KEY'] = 'your-secret-api-key-here'
result = await get_chemicals_list_tool(
    chemName="滴滴涕",
    chemCas="50-29-3"
)
```

### JWT Token 认证

**服务器端配置：**
```env
JWT_SECRET=your-jwt-secret-key-here
```

**客户端使用：**
```python
import jwt
from datetime import datetime, timedelta

# 创建JWT Token
def create_token(user_id: str, expires_in: int = 3600):
    payload = {
        'sub': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, 'your-jwt-secret-key-here', algorithm='HS256')

# 使用Token调用API
token = create_token("user123")
result = await get_chemicals_list_tool(
    chemName="滴滴涕",
    chemCas="50-29-3",
    token=token
)
```

## 🛡️ 速率限制

系统内置速率限制功能，默认配置：
- 每小时最多50次调用
- 按工具类型分别计数

可以通过环境变量修改：
```env
RATE_LIMIT_MAX_CALLS=100    # 每小时最多100次
RATE_LIMIT_WINDOW=3600      # 时间窗口：3600秒（1小时）
```

## 🔍 测试验证

运行测试脚本验证身份验证功能：
```bash
python test_auth.py
```

预期输出：
```
=== MCP服务器身份验证测试 ===

1. 测试API Key认证...
✓ API Key认证成功

2. 测试错误的API Key...
✓ 正确拒绝错误API Key: Invalid API Key

3. 测试JWT Token认证...
✓ JWT Token认证成功

4. 测试错误的JWT Token...
✓ 正确拒绝错误Token: Invalid JWT Token

5. 测试无认证信息...
✓ 正确要求认证: Authentication required

6. 测试化学品详情工具认证...
✓ 化学品详情工具认证成功

=== 测试完成 ===
```

## 🔐 安全最佳实践

### 1. API Key 管理
- 使用强随机密钥（至少32位字符）
- 定期更换API Key
- 不同的环境使用不同的Key（开发、测试、生产）
- 将密钥存储在安全的环境变量中，不要硬编码在代码里

### 2. JWT Token 安全
- 使用强密钥签名JWT
- 设置合理的过期时间（建议15分钟到1小时）
- 不要在JWT中存储敏感信息
- 使用HTTPS传输Token

### 3. 监控和日志
- 定期检查认证失败日志
- 监控异常访问模式
- 设置告警机制

### 4. 生产环境建议
```env
# 生产环境配置示例
MCP_API_KEY=sk_prod_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
JWT_SECRET=prod_jwt_secret_key_at_least_256_bits_long_for_hs256_algorithm
RATE_LIMIT_MAX_CALLS=100
RATE_LIMIT_WINDOW=3600
MCP_LOG_LEVEL=WARNING
```

## 🛠️ 故障排查

### 常见问题

**1. 认证失败但密钥正确**
- 检查环境变量是否正确设置
- 确认密钥前后没有空格
- 检查日志中的详细错误信息

**2. JWT Token无效**
- 确认JWT密钥匹配
- 检查Token是否过期
- 验证JWT格式是否正确

**3. 速率限制异常**
- 检查RATE_LIMIT配置
- 确认没有其他客户端占用配额
- 等待时间窗口重置

### 调试模式

临时启用调试日志：
```env
MCP_LOG_LEVEL=DEBUG
```

## 📚 相关文档

- [FastMCP官方文档](https://gofastmcp.com/)
- [JWT官方规范](https://jwt.io/)
- [Python-JWT库文档](https://pyjwt.readthedocs.io/)

## 🔗 示例代码

查看完整的示例代码：
- `auth_middleware.py` - 认证中间件实现
- `test_auth.py` - 认证测试脚本
- `nrcc-search.py` - 主要的MCP服务器代码

---

如有问题，请查看日志文件或联系系统管理员。