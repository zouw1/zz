from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 安全配置
SECRET_KEY = "your-secret-key"  # 在生产环境中应使用环境变量
ALGORITHM = "HS256"          # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 改为24小时

# 创建安全验证器
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    Returns:
        编码后的JWT字符串
    """
    to_encode = data.copy()
    # 设置令牌过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # 生成JWT令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    验证JWT令牌
    Args:
        credentials: HTTP认证凭证
    Returns:
        解码后的令牌数据
    Raises:
        HTTPException: 当令牌无效或过期时
    """
    try:
        # 解码并验证令牌
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭证") 