from pydantic import BaseModel

# 定义图像生成请求的数据模型
class ImageGenerationRequest(BaseModel):
    """
    图像生成请求的数据模型
    Attributes:
        prompt: 主要提示词，用于描述要生成的图像
        prompt2: 辅助提示词，用于提供额外的细节（可选）
        width: 图像宽度（像素）
        height: 图像高度（像素）
        steps: 生成步数，影响生成质量，默认20步
    """
    prompt: str                # 主要提示词
    prompt2: str = ""         # 辅助提示词(可选)
    width: int                # 图像宽度
    height: int               # 图像高度
    steps: int = 20          # 生成步数,默认20步 

# 用户注册请求模型
class UserCreate(BaseModel):
    """
    用户注册请求模型
    Attributes:
        username: 用户名
        password: 密码
        email: 邮箱
    """
    username: str
    password: str
    email: str    # 添加邮箱字段

# 用户登录请求模型
class UserLogin(BaseModel):
    """
    用户登录请求模型
    Attributes:
        email: 邮箱
        password: 密码
    """
    email: str
    password: str

# 用户响应模型
class UserResponse(BaseModel):
    """
    用户响应模型
    Attributes:
        username: 用户名
        token: JWT访问令牌
    """
    username: str
    token: str

# 添加密码重置请求模型
class PasswordResetRequest(BaseModel):
    email: str

# 添加密码重置验证模型
class PasswordReset(BaseModel):
    token: str
    new_password: str 