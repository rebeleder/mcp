# NRCC Search

国家危险化学品数据库搜索工具 - Model Context Protocol (MCP) Server

## 项目简介

这是一个基于 MCP (Model Context Protocol) 的服务器应用，提供国家危险化学品数据库的搜索功能。支持通过化学品名称和 CAS 号搜索化学品列表及详细信息。

## 功能特性

- 🔍 化学品列表搜索（支持模糊查询）
- 📊 化学品详细信息查询
- ⏱️ 请求速率限制（每小时50次调用）
- 🚀 基于 FastMCP 的高性能服务器

## 项目结构

```
nrcc-search/
├── src/
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   └── nrcc_search.py      # MCP 工具和服务器实现
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       └── middleware.py       # 速率限制中间件
├── tests/                      # 测试文件
│   └── __init__.py
├── docs/                       # 文档
├── main.py                     # 主入口文件
├── pyproject.toml              # 项目配置和依赖
├── .env.example                # 环境变量示例
├── .gitignore                  # Git 忽略文件
├── README.md                   # 项目说明
└── ARCHITECTURE.md             # 架构文档
```

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd nrcc-search

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装生产环境依赖
make install
# 或
pip install -e .

# 安装开发环境依赖
make install-dev
# 或
pip install -e ".[dev]"
```

### 环境配置

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件（可选）：

```env
# 速率限制配置（在代码中默认为每小时50次）
# RATE_LIMIT_MAX_CALLS=50
# RATE_LIMIT_WINDOW=3600
```

## 使用方法

### 启动服务器

```bash
# 使用 Makefile
make run

# 或直接运行
python main.py
```

### API 使用示例

#### 1. 搜索化学品列表

```python
from nrcc_search import get_chemicals_list_tool

# 使用 API Key 认证
result = await get_chemicals_list_tool(
    chemName="滴滴涕",
    chemCas="50-29-3",
    api_key="your-api-key"
)
print(result)
```

#### 2. 获取化学品详情

```python
from nrcc_search import get_chemical_detail_tool

# 使用 JWT Token 认证
result = await get_chemical_detail_tool(
    chem_id="82861C0E-1391-4E10-8AAF-6C342C59EB92",
    token="your-jwt-token"
)
print(result)
```

### 作为 MCP Server 使用

服务器默认运行在 `http://localhost:8000`，支持 streamable-http 传输协议。

## 开发

### 运行测试

```bash
# 使用 Makefile
make test

# 或直接使用 pytest
pytest tests/ -v
```

### 代码格式化

```bash
# 使用 black 和 isort 格式化代码
make format
```

### 代码检查

```bash
# 使用 mypy 进行类型检查
make lint
```

### 清理构建文件

```bash
make clean
```

## 认证机制

### API Key 认证

在请求中提供 `api_key` 参数：

```python
result = await get_chemicals_list_tool(
    chemName="苯",
    chemCas="71-43-2",
    api_key="your-api-key"
)
```

### JWT Token 认证

在请求中提供 `token` 参数：

```python
result = await get_chemical_detail_tool(
    chem_id="chemical-id",
    token="your-jwt-token"
)
```

### 速率限制

默认配置：每小时 50 次请求。可通过环境变量调整。

## 依赖项

### 生产环境

- `httpx>=0.28.1` - HTTP 客户端
- `mcp[cli]>=1.21.0` - MCP 框架
- `python-dotenv>=1.0.0` - 环境变量管理
- `pyjwt>=2.8.0` - JWT 认证

### 开发环境

- `pytest>=7.0.0` - 测试框架
- `pytest-asyncio>=0.21.0` - 异步测试支持
- `black>=23.0.0` - 代码格式化
- `isort>=5.12.0` - 导入排序
- `mypy>=1.0.0` - 类型检查

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关文档

- [架构文档](ARCHITECTURE.md)
- [任务清单](TODO.md)
