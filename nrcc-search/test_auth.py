#!/usr/bin/env python3
"""
MCP服务器身份验证测试脚本
"""
import asyncio
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

# 设置测试环境
os.environ['MCP_API_KEY'] = 'test-api-key-123'
os.environ['JWT_SECRET'] = 'test-jwt-secret-456'

from nrcc_search import get_chemicals_list_tool, get_chemical_detail_tool, AuthenticationError

def create_test_token(user_id: str = "test_user", expires_in: int = 3600) -> str:
    """创建测试JWT令牌"""
    payload = {
        'sub': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')

async def test_authentication():
    """测试身份验证功能"""
    print("=== MCP服务器身份验证测试 ===\n")

    # 测试1: API Key认证
    print("1. 测试API Key认证...")
    try:
        result = await get_chemicals_list_tool(
            chemName="滴滴涕",
            chemCas="50-29-3",
            api_key="test-api-key-123"
        )
        print("✓ API Key认证成功")
    except AuthenticationError as e:
        print(f"✗ API Key认证失败: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")

    # 测试2: 错误的API Key
    print("\n2. 测试错误的API Key...")
    try:
        result = await get_chemicals_list_tool(
            chemName="滴滴涕",
            chemCas="50-29-3",
            api_key="wrong-api-key"
        )
        print("✗ 应该认证失败但没有")
    except AuthenticationError as e:
        print(f"✓ 正确拒绝错误API Key: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")

    # 测试3: JWT Token认证
    print("\n3. 测试JWT Token认证...")
    token = create_test_token("test_user")
    try:
        result = await get_chemicals_list_tool(
            chemName="滴滴涕",
            chemCas="50-29-3",
            token=token
        )
        print("✓ JWT Token认证成功")
    except AuthenticationError as e:
        print(f"✗ JWT Token认证失败: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")

    # 测试4: 错误的JWT Token
    print("\n4. 测试错误的JWT Token...")
    try:
        result = await get_chemicals_list_tool(
            chemName="滴滴涕",
            chemCas="50-29-3",
            token="wrong-token"
        )
        print("✗ 应该认证失败但没有")
    except AuthenticationError as e:
        print(f"✓ 正确拒绝错误Token: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")

    # 测试5: 无认证信息
    print("\n5. 测试无认证信息...")
    try:
        result = await get_chemicals_list_tool(
            chemName="滴滴涕",
            chemCas="50-29-3"
        )
        print("✗ 应该认证失败但没有")
    except AuthenticationError as e:
        print(f"✓ 正确要求认证: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")

    # 测试6: 化学品详情工具认证
    print("\n6. 测试化学品详情工具认证...")
    try:
        result = await get_chemical_detail_tool(
            chem_id="82861C0E-1391-4E10-8AAF-6C342C59EB92",
            api_key="test-api-key-123"
        )
        print("✓ 化学品详情工具认证成功")
    except AuthenticationError as e:
        print(f"✗ 化学品详情工具认证失败: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_authentication())